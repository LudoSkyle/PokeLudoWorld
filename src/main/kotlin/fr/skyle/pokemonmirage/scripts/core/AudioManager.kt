package fr.skyle.pokemonmirage.scripts.core

import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.AudioServer
import godot.api.AudioStream
import godot.api.AudioStreamMP3
import godot.api.AudioStreamPlayer
import godot.api.Node
import godot.api.ResourceLoader
import kotlin.math.log10
import kotlin.math.max
import kotlin.math.min

/**
 * Le son du jeu, en trois sortes :
 *
 * - la **musique** du lieu, en boucle. Elle arrive toujours en fondu, et en
 *   changer est un **fondu enchaîné** : l'ancienne s'éteint pendant que la
 *   nouvelle monte, sur [fadeSeconds] ;
 * - les **jingles** (objet reçu, cloche) : la musique se met en pause, le
 *   jingle joue, la musique reprend là où elle en était ;
 * - les **bruitages** (curseur, mur, porte) : ils passent par-dessus la
 *   musique sans y toucher.
 *
 * Un son se désigne par le nom de son fichier, sans extension, dans
 * `assets/audio/music`, `jingles` ou `sfx` ; il peut être en WAV, OGG ou MP3.
 */
@Script
class AudioManager : Node() {

	companion object {
		var instance: AudioManager? = null
			private set

		private const val DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/audio/"
		private const val SFX_VOICES = 4
		private const val SILENT_DB = -60.0
		private val FORMATS = listOf("wav", "ogg", "mp3")
	}

	/**
	 * Durée d'un fondu de musique, en secondes : celui qui fait monter une
	 * musique qui démarre, et celui qui éteint celle qu'elle remplace. Les deux
	 * se font en même temps.
	 */
	@Category("Musique")
	@Export
	var fadeSeconds: Double = 1.0

	/** La musique qui monte ou qui joue, et celle qui s'éteint : deux lecteurs qui échangent leurs rôles. */
	private var music: AudioStreamPlayer? = null
	private var outgoing: AudioStreamPlayer? = null
	private var jinglePlayer: AudioStreamPlayer? = null
	private var voices: List<AudioStreamPlayer> = emptyList()
	private var cryPlayer: AudioStreamPlayer? = null
	private var lastCry = ""
	private var cryCount = 0
	private var cryVolume = 1.0
	private val streams = HashMap<String, AudioStream?>()

	/** La musique demandée : celle qu'on entend, ou qu'on entendra après le jingle. */
	private var wanted = ""

	/** Celle que joue [music], et celle que [outgoing] finit d'éteindre. */
	private var playing = ""
	private var leaving = ""

	/** Le volume de chacune, de 0 (silence) à 1. */
	private var level = 1.0
	private var leavingLevel = 0.0

	private var jingleActive = false
	private var lastJingle = ""
	private var lastSfx = ""
	private var starts = 0
	private var sfxCount = 0

	/** Vrai tant qu'un jingle joue : la musique est en pause, le dialogue attend. */
	val isJinglePlaying: Boolean
		get() = jingleActive

	@Register
	override fun _ready() {
		instance = this
		music = player("Music")
		outgoing = player("MusicOut")
		jinglePlayer = player("Jingle")
		voices = (0 until SFX_VOICES).map { player("Sfx$it") }
		cryPlayer = player("Cry")

		applyVolumes()

		// Les tests jouent le jeu pour de vrai, mais en silence.
		if (GameFiles.testing) AudioServer.setBusMute(0, true)

		Logger.i("Loading audio manager ...")
	}

	private fun musicGain(): Double = Settings.gain(Settings.Volume.MUSIC)

	/**
	 * Applique les volumes réglés par le joueur (voir [Settings]) à ce qui joue
	 * déjà : la musique, tout de suite ; bruitages et jingles gardent le leur
	 * d'un son à l'autre. Les cris prennent le leur à chaque cri. À appeler
	 * quand un réglage change.
	 */
	fun applyVolumes() {
		Settings.load()
		val sounds = decibels(Settings.gain(Settings.Volume.SOUNDS)).toFloat()
		voices.forEach { it.volumeDb = sounds }
		jinglePlayer?.volumeDb = sounds
		cryPlayer?.volumeDb = decibels(cryVolume * Settings.gain(Settings.Volume.CRIES)).toFloat()          // le cri en cours suit, lui aussi
		music?.volumeDb = decibels(level * musicGain()).toFloat()
		if (leaving.isNotEmpty()) outgoing?.volumeDb = decibels(leavingLevel * musicGain()).toFloat()
	}

	/** Le volume, en décibels, auquel jouent la musique, les bruitages et le dernier cri : ce que les tests écoutent. */
	@Register
	fun musicDb(): Double = music?.volumeDb?.toDouble() ?: 0.0

	@Register
	fun soundsDb(): Double = voices.firstOrNull()?.volumeDb?.toDouble() ?: 0.0

	@Register
	fun cryDb(): Double = cryPlayer?.volumeDb?.toDouble() ?: 0.0

	private fun player(name: String): AudioStreamPlayer {
		val node = AudioStreamPlayer()
		node.setName(name)
		addChild(node)
		return node
	}

	@Register
	override fun _process(delta: Double) {
		if (jingleActive && jinglePlayer?.playing != true) {
			jingleActive = false
			// La musique reprend où elle en était — ou c'est une autre qui démarre,
			// si l'on a changé de lieu pendant le jingle.
			if (wanted == playing) music?.streamPaused = false else change(wanted)
		}
		if (jingleActive) return

		val step = if (fadeSeconds > 0.0) delta / fadeSeconds else 1.0

		// Celle qui arrive monte.
		if (level < 1.0) {
			level = min(level + step, 1.0)
			music?.volumeDb = decibels(level * musicGain()).toFloat()
		}
		// Celle qui part s'éteint, puis se tait pour de bon.
		if (leaving.isNotEmpty()) {
			leavingLevel -= step
			if (leavingLevel <= 0.0) silence() else outgoing?.volumeDb = decibels(leavingLevel * musicGain()).toFloat()
		}
	}

	/**
	 * Demande la musique [id] ; une chaîne vide demande le silence. Sans effet
	 * si c'est déjà elle : passer d'une carte à l'autre du même lieu ne la
	 * relance pas.
	 */
	fun playMusic(id: String) {
		if (id == wanted) return
		wanted = id
		// Pendant un jingle rien ne bouge : le jingle fini, c'est la nouvelle qui démarrera.
		if (!jingleActive) change(id)
	}

	/**
	 * Passe à la musique [id] en fondu enchaîné : celle qui jouait devient
	 * celle qui part, et s'éteint à partir du volume qu'elle avait ; l'autre
	 * lecteur fait monter la nouvelle depuis le silence.
	 */
	private fun change(id: String) {
		if (id == playing) return

		// On revient à la musique qui était en train de s'éteindre : elle n'a
		// pas à repartir du début, les deux échangent simplement leurs rôles.
		if (id.isNotEmpty() && id == leaving) {
			swap()
			music?.streamPaused = false
			return
		}

		// Celle qui finissait de s'éteindre est coupée : il n'y a que deux lecteurs.
		silence()
		swap()

		val out = music ?: return
		out.stop()
		out.streamPaused = false
		playing = id
		level = if (fadeSeconds > 0.0) 0.0 else 1.0
		out.volumeDb = decibels(level * musicGain()).toFloat()
		if (id.isEmpty()) return

		val stream = load("music/$id") ?: return
		(stream as? AudioStreamMP3)?.loop = true
		out.stream = stream
		out.play()
		starts++
	}

	/** Les deux lecteurs échangent leurs rôles, chacun gardant son volume du moment. */
	private fun swap() {
		val was = music
		music = outgoing
		outgoing = was

		val id = playing
		playing = leaving
		leaving = id

		val volume = level
		level = leavingLevel
		leavingLevel = volume
		// Rien ne jouait : il n'y a rien à éteindre.
		if (leaving.isEmpty()) leavingLevel = 0.0
	}

	/** Fait taire la musique qui partait. */
	private fun silence() {
		outgoing?.stop()
		leaving = ""
		leavingLevel = 0.0
	}

	/** Met la musique en pause, joue le jingle [id], puis la laisse reprendre. */
	fun jingle(id: String) {
		val out = jinglePlayer ?: return
		val stream = load("jingles/$id") ?: return
		(stream as? AudioStreamMP3)?.loop = false

		// Le jingle coupe court au fondu : la musique qui partait se tait, l'autre attend.
		silence()
		music?.streamPaused = true
		out.stream = stream
		out.play()
		jingleActive = true
		lastJingle = id
	}

	/** Joue le bruitage [id] par-dessus tout le reste. */
	fun sfx(id: String) {
		val stream = load("sfx/$id") ?: return
		val voice = voices.firstOrNull { !it.playing } ?: voices.firstOrNull() ?: return
		voice.stream = stream
		voice.play()
		lastSfx = id
		sfxCount++
	}

	/**
	 * Fait entendre le cri du Pokémon [species] (`cries/<species>`), au volume
	 * [volume] de 0 à 1. Un seul cri à la fois : si un autre joue encore, celui-ci
	 * est passé sous silence et la fonction renvoie false — deux oiseaux qui
	 * crient ensemble ne se couvrent pas.
	 */
	fun cry(species: String, volume: Double = 1.0): Boolean {
		val voice = cryPlayer ?: return false
		if (voice.playing) return false
		val stream = load("cries/$species") ?: return false
		voice.stream = stream
		cryVolume = volume
		voice.volumeDb = decibels(volume * Settings.gain(Settings.Volume.CRIES)).toFloat()
		voice.play()
		lastCry = species
		cryCount++
		return true
	}

	/** Le son nommé [path], sans extension : le premier format trouvé parmi [FORMATS]. */
	private fun load(path: String): AudioStream? = streams.getOrPut(path) {
		val file = FORMATS.map { "$DIR$path.$it" }.firstOrNull { ResourceLoader.exists(it) }
		(file?.let { ResourceLoader.load(it) } as? AudioStream).also {
			if (it == null) Logger.e("Son introuvable : $path")
		}
	}

	/** Volume en décibels pour une fraction de 0 à 1. */
	private fun decibels(fraction: Double): Double =
		if (fraction <= 0.001) SILENT_DB else max(SILENT_DB, 20.0 * log10(fraction))

	// --- vu de Godot : ce que les tests écoutent

	/** La musique demandée pour le lieu. */
	@Register
	fun musicId(): String = wanted

	/** Vrai si la musique sort vraiment : ni en pause, ni arrêtée. */
	@Register
	fun musicAudible(): Boolean = music?.playing == true && music?.streamPaused != true

	/** Le volume de la musique qui joue, de 0 à 1 : il monte pendant son fondu d'arrivée. */
	@Register
	fun musicLevel(): Double = level

	/** La musique qui finit de s'éteindre, et son volume ; vide et 0 hors d'un fondu enchaîné. */
	@Register
	fun leavingId(): String = leaving

	@Register
	fun leavingLevel(): Double = leavingLevel

	/** Nombre de fois où une musique a démarré depuis le lancement. */
	@Register
	fun musicStarts(): Int = starts

	@Register
	fun jinglePlaying(): Boolean = jingleActive

	@Register
	fun lastJingleId(): String = lastJingle

	@Register
	fun lastSfxId(): String = lastSfx

	@Register
	fun sfxPlayed(): Int = sfxCount

	@Register
	fun lastCryId(): String = lastCry

	@Register
	fun criesPlayed(): Int = cryCount
}
