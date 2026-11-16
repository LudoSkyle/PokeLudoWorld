package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryText
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import fr.skyle.pokeludoworld.scripts.ui.T
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
import godot.annotation.Register
import godot.annotation.Script
import godot.api.StaticBody2D
import godot.core.PackedStringArray
import java.time.LocalTime

/**
 * Meuble qu'on peut examiner : bibliothèque, poubelle, serveur, télé, horloge.
 *
 * Le meuble lui-même reste une tuile ; ceci est un corps invisible posé sur sa
 * case, que le joueur trouve par la requête physique devant lui. Contrairement
 * à un panneau, ce qu'il dit peut dépendre du moment : l'heure, une émission,
 * l'avancée de l'histoire.
 *
 * Avec `kind = item`, c'est une **trouvaille** : la première fois, il dit
 * [text] — dont une boîte donne l'objet par `@give:` — et pose [flag]. Ensuite
 * il ne dit plus que ses [states] ; s'il n'en a pas, il quitte la carte dès
 * qu'on l'a prise.
 *
 * Une trouvaille qui attend un drapeau ([requiredFlag]) **apparaît dès qu'il
 * est posé**, sans recharger la carte : jusque-là elle est sur la carte mais
 * cachée, et l'on ne trouve rien à sa place. C'est ainsi qu'un personnage peut
 * dire où chercher, sur la carte même où se trouve l'objet.
 */
@Script
class Readable : StaticBody2D() {

	/** `text` (défaut), `clock`, `tv` ou `item`. */
	@Category("Contenu")
	@Export
	var kind: String = "text"

	/** Pour `kind = text` ou `item`. Une barre verticale `|` sépare deux boîtes. */
	@Category("Contenu")
	@MultilineText
	@Export
	var text: String = ""

	/**
	 * Pour `kind = text` ou `item` : ce qu'il dit selon l'histoire : des entrées `drapeau > texte`, lues de
	 * bas en haut. [text] reste le défaut (voir StoryText).
	 */
	@Category("Contenu")
	@Export
	var states: PackedStringArray = PackedStringArray()

	/**
	 * Question Oui / Non posée avant d'agir : `Question ?` devant [text],
	 * `drapeau > Question ?` devant le texte de cet état. Non ne dit rien.
	 */
	@Category("Contenu")
	@Export
	var ask: String = ""

	/** Pour `kind = item` : le drapeau posé par la trouvaille. Un par trouvaille. */
	@Category("Contenu")
	@Export
	var flag: String = ""

	/** Drapeau sans lequel le meuble n'est pas sur la carte. Une trouvaille, elle, l'attend cachée. */
	@Category("Histoire")
	@Export
	var requiredFlag: String = ""

	/** Drapeau avec lequel le meuble n'est plus sur la carte. */
	@Category("Histoire")
	@Export
	var forbiddenFlag: String = ""

	/** Vrai tant qu'une trouvaille attend son drapeau, cachée : on ne la trouve pas. */
	private var waiting = false

	/** Sa couche de collision, mise de côté pendant qu'elle attend. */
	private var layer = 0L

	@Register
	override fun _ready() {
		if (!StoryFlags.allows(requiredFlag, forbiddenFlag)) {
			// Une trouvaille dont le drapeau n'est pas encore posé reste là, cachée,
			// et se montrera dès qu'il le sera (voir _process).
			if (kind == ITEM && requiredFlag.isNotBlank() && StoryFlags.allows("", forbiddenFlag)) {
				waiting = true
				layer = getCollisionLayer()
				setCollisionLayer(0)
				visible = false
				setProcess(true)
				return
			}
			// Absent de cette étape de l'histoire : il quitte la carte avant d'y avoir servi.
			queueFree()
			return
		}
		// Seule une trouvaille sans suite guette le moment où on la prend.
		setProcess(kind == ITEM && states.size == 0)
		if (kind != ITEM) return

		if (flag.isBlank()) Logger.e("Trouvaille sans drapeau : ${name}")
		if (!text.contains("@give:")) Logger.e("Trouvaille qui ne donne rien (pas de @give:) : ${name}")
	}

	/** Ramassée, et plus rien à en dire : elle quitte la carte, sa case se libère. */
	@Register
	override fun _process(delta: Double) {
		if (waiting) {
			if (!StoryFlags.allows(requiredFlag, forbiddenFlag)) return
			// Son drapeau vient d'être posé : elle se montre, et on peut la trouver.
			waiting = false
			setCollisionLayer(layer)
			visible = true
			setProcess(states.size == 0)
			return
		}
		if (isTaken) queueFree()
	}

	fun read() {
		when (kind) {
			"clock" -> {
				val now = LocalTime.now()
				MessageBox.instance?.play(listOf(T("L'horloge indique %d h %02d.").format(now.hour, now.minute)))
			}

			"tv" -> MessageBox.instance?.play(StoryText.boxes(TV_PROGRAMS.random()))
			ITEM -> find()
			else -> StoryText.say(text, states, ask)
		}
	}

	private val isTaken: Boolean
		get() = flag.isNotBlank() && StoryFlags.has(flag)

	/**
	 * La trouvaille : son drapeau est posé par la première boîte, donc après
	 * un Oui s'il y a une question. Une fois prise, [text] ne se redit plus.
	 */
	private fun find() {
		if (isTaken) {
			StoryText.say("", states, ask)
			return
		}

		StoryText.say("@flag:$flag $text", states, ask)
	}

	companion object {
		private const val ITEM = "item"

		/**
		 * Dans l'esprit des jeux d'origine : la télé décrit en une phrase ce
		 * qui passe, et le héros repart. Aucun Pokémon pour l'instant.
		 */
		// i18n
		private val TV_PROGRAMS = listOf(
			"C'est la météo.|Grand soleil sur tout le village aujourd'hui !",
			"C'est la météo.|Quelques nuages ce soir, mais pas une goutte de pluie.",
			"C'est la météo.|Un petit vent frais soufflera sur la côte demain matin.",
			"Il y a un film à la télé.|Quatre garçons marchent le long d'une voie ferrée.|Je ferais mieux d'y aller aussi.",
			"Il y a un film à la télé.|Deux hommes dansent sur un piano géant.|Bon, il est temps de bouger !",
			"Une émission de cuisine.|Le chef rate sa crêpe, le public applaudit quand même.",
			"Un documentaire sur les grottes de la région.|Il paraît qu'on s'y perd facilement.",
			"Un jeu télévisé.|Le candidat hésite... Ah, mauvaise réponse !",
			"C'est le journal.|Rien à signaler au village, et c'est très bien comme ça.",
			"Une publicité pour des chaussures de course.|Avec elles on irait deux fois plus vite, paraît-il.",
		)
	}
}
