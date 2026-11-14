package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.log.Logger
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

/**
 * Le son du jeu, en trois sortes :
 *
 * - la **musique** du lieu, en boucle. En changer se fait par un fondu très
 *   court de l'ancienne, puis la nouvelle démarre aussitôt ;
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

		private const val DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/audio/"
		private const val SFX_VOICES = 4
		private const val SILENT_DB = -60.0
		private val FORMATS = listOf("wav", "ogg", "mp3")
	}

	/** Durée du fondu de sortie d'une musique, en secondes. */
	@Category("Musique")
	@Export
	var fadeSeconds: Double = 0.3

	private var music: AudioStreamPlayer? = null
	private var jinglePlayer: AudioStreamPlayer? = null
	private var voices: List<AudioStreamPlayer> = emptyList()
	private val streams = HashMap<String, AudioStream?>()

	/** La musique demandée : celle qu'on entend, ou qu'on entendra après le fondu ou le jingle. */
	private var wanted = ""

	/** Celle qui sort réellement du haut-parleur. */
	private var playing = ""
	private var fading = false
	private var fadeLeft = 0.0

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
		jinglePlayer = player("Jingle")
		voices = (0 until SFX_VOICES).map { player("Sfx$it") }

		// Les tests jouent le jeu pour de vrai, mais en silence.
		if (GameFiles.testing) AudioServer.setBusMute(0, true)

		Logger.i("Loading audio manager ...")
	}

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
			if (wanted == playing) music?.streamPaused = false else start(wanted)
		}

		if (!fading) return
		fadeLeft -= delta
		if (fadeLeft <= 0.0) {
			fading = false
			start(wanted)
		} else {
			music?.volumeDb = decibels(fadeLeft / fadeSeconds).toFloat()
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

		when {
			// Le jingle fini, c'est la nouvelle qui démarrera.
			jingleActive -> {}
			music?.playing == true && fadeSeconds > 0.0 -> {
				if (!fading) {
					fading = true
					fadeLeft = fadeSeconds
				}
			}
			else -> start(id)
		}
	}

	private fun start(id: String) {
		val out = music ?: return
		fading = false
		out.stop()
		out.streamPaused = false
		out.volumeDb = 0.0f
		playing = id
		if (id.isEmpty()) return

		val stream = load("music/$id") ?: return
		(stream as? AudioStreamMP3)?.loop = true
		out.stream = stream
		out.play()
		starts++
	}

	/** Met la musique en pause, joue le jingle [id], puis la laisse reprendre. */
	fun jingle(id: String) {
		val out = jinglePlayer ?: return
		val stream = load("jingles/$id") ?: return
		(stream as? AudioStreamMP3)?.loop = false

		fading = false
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
}
