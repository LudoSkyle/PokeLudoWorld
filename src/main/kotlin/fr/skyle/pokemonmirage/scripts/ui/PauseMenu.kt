package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.core.DayNight
import fr.skyle.pokemonmirage.scripts.core.Weather
import fr.skyle.pokemonmirage.scripts.gameplay.items.Inventory
import fr.skyle.pokemonmirage.scripts.gameplay.items.Items
import fr.skyle.pokemonmirage.scripts.gameplay.story.Quest
import fr.skyle.pokemonmirage.scripts.gameplay.story.Quests
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.NinePatchRect
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.core.Vector2

/**
 * Menu de pause : une colonne d'entrées en haut à droite, un curseur en début
 * de ligne.
 *
 * Comme la boîte de dialogue, il ne décide pas seul de s'ouvrir et ne lit
 * jamais la touche d'interaction : c'est le joueur qui l'ouvre et lui passe
 * la main à chaque image avec [handle]. Tant qu'il est ouvert, le monde est
 * figé (voir Player et Npc).
 *
 * Les entrées sont les enfants de `Control/Menu/Entries`, dans l'ordre. En
 * ajouter une, c'est ajouter un Label dans la scène et un cas dans [confirm].
 */
@Script
class PauseMenu : CanvasLayer() {

	companion object {
		var instance: PauseMenu? = null
			private set

		const val ACTION = "menu"
	}

	/** Cadre : nom d'un fichier de `assets/ui/frames`, sans l'extension. */
	@Category("Affichage")
	@Export
	var frame: String = "rse_01"

	private var menu: Control? = null
	private var cursor: Control? = null
	private var entries: List<Control> = emptyList()

	/** Les outils de l'entrée Debug, dans une boîte de choix qui change de contenu d'une page à l'autre. */
	private var debugChoices: ChoiceBox? = null
	private var debugPage = DebugPage.TOOLS
	private var debugQuest: Quest? = null

	/** Entrée sous le curseur. Revient à la première à chaque ouverture. */
	var selected: Int = 0
		private set

	/** Vrai du moment où le menu s'ouvre à celui où il se ferme, écrans compris. */
	var isOpen: Boolean = false
		private set

	/** Nom du nœud de l'entrée sous le curseur : `Bag`, `Options`, `Quit`. */
	val selectedName: String
		get() = entries.getOrNull(selected)?.name?.toString() ?: ""

	@Register
	override fun _ready() {
		instance = this
		menu = getNode("Control/Menu") as? Control
		cursor = getNode("Control/Menu/Cursor") as? Control

		val list = getNode("Control/Menu/Entries")
		entries = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Control }

		val texture = ResourceLoader.load("$FRAMES_DIR$frame.png") as? Texture2D
		if (texture == null) {
			Logger.e("Cadre de menu inconnu : $frame")
		} else {
			(getNode("Control/Menu/Frame") as? NinePatchRect)?.texture = texture
		}

		debugChoices = getNode("Control/DebugChoices") as? ChoiceBox

		PixelShadow.attachAll(menu)
		menu?.visible = false
	}

	fun open() {
		if (isOpen || entries.isEmpty()) return
		// Chaque ouverture repart de la première entrée.
		selected = 0
		isOpen = true
		menu?.visible = true
		placeCursor()
	}

	fun close() {
		isOpen = false
		debugChoices?.close()
		menu?.visible = false
	}

	/**
	 * Cache ou remontre le panneau sans fermer le menu : l'écran de sauvegarde
	 * prend sa place à l'écran, puis la lui rend si l'on répond Non.
	 */
	fun showPanel(shown: Boolean) {
		if (isOpen) menu?.visible = shown
	}

	/**
	 * À appeler à chaque image tant que le menu est ouvert. [interact] est la
	 * pression d'interaction lue par le joueur.
	 */
	fun handle(interact: Boolean) {
		if (!isOpen) return

		// Un écran ouvert depuis le menu prend la main, et la rend en se fermant.
		val options = OptionsMenu.instance
		if (options != null && options.isOpen) {
			options.handle(interact)
			return
		}

		val bag = BagMenu.instance
		if (bag != null && bag.isOpen) {
			bag.handle(interact)
			return
		}

		val dex = PokedexDebug.instance
		if (dex != null && dex.isOpen) {
			dex.handle(interact)
			return
		}

		val save = SaveMenu.instance
		if (save != null && save.isOpen) {
			save.handle(interact)
			return
		}

		val tools = debugChoices
		if (tools != null && tools.isOpen) {
			// Retour, ou la touche du menu, remonte d'une page ; depuis la première, referme la boîte.
			val choice = tools.handle(interact) ?: return
			when (debugPage) {
				DebugPage.TOOLS -> when (choice) {
					TOOL_BAG -> fillBag()
					TOOL_QUESTS -> showQuests()
					TOOL_TIME -> {
						// L'heure change sur place : la boîte reste ouverte, sur la même ligne.
						DayNight.cycle()
						tools.relabel(TOOL_TIME, T(DayNight.label()))
					}

					TOOL_WEATHER -> {
						// Le temps qu'il fait défile de la même façon, sans fermer la boîte.
						Weather.cycle()
						tools.relabel(TOOL_WEATHER, T(Weather.label()))
					}
					TOOL_DEX -> {
						// La vue de debug du Pokédex national prend tout l'écran : la boîte se referme derrière elle.
						tools.close()
						PokedexDebug.instance?.open()
					}
					else -> tools.close()
				}
				DebugPage.QUESTS -> Quests.ALL.getOrNull(choice)?.let { showActions(it) } ?: showTools()
				DebugPage.ACTIONS -> when (choice) {
					ACTION_RESET -> debugQuest?.let { resetQuest(it) }
					ACTION_NEXT -> debugQuest?.let { advanceQuest(it, all = false) }
					ACTION_FINISH -> debugQuest?.let { advanceQuest(it, all = true) }
					else -> showQuests()
				}
			}
			return
		}

		// La touche qui a ouvert le menu le referme.
		if (Input.isActionJustPressed(ACTION)) {
			close()
			return
		}

		if (MenuKeys.down()) move(1)
		if (MenuKeys.up()) move(-1)
		if (interact) confirm()
	}

	/** Le curseur boucle : Haut sur la première entrée mène à la dernière. */
	private fun move(step: Int) {
		selected = (selected + step + entries.size) % entries.size
		placeCursor()
	}

	private fun confirm() {
		when (selectedName) {
			"Quit" -> close()
			"Options" -> OptionsMenu.instance?.open()
			"Save" -> SaveMenu.instance?.open()
			"Bag" -> BagMenu.instance?.open()
			"Debug" -> debug()
			else -> Logger.i("Menu : entree inconnue $selectedName")
		}
	}

	/**
	 * Outils de mise au point : une boîte de choix à trois pages. La première
	 * liste les outils ; « Quêtes » ouvre la liste des quêtes ; en choisir une
	 * ouvre ce qu'on peut lui faire — repartir de zéro, franchir une étape, la
	 * finir. Une quête de plus n'ajoute qu'une ligne à la deuxième page.
	 * Les lignes de l'heure et de la météo font défiler, à chaque validation,
	 * les moments de la journée et les temps qu'il peut faire.
	 */
	private fun debug() = showTools()

	private fun showTools() {
		debugPage = DebugPage.TOOLS
		debugChoices?.open(
			listOf(T(DEBUG_BAG_LABEL), T(DEBUG_QUESTS_LABEL), T(DayNight.label()), T(Weather.label()), T(DEBUG_DEX_LABEL), T(DEBUG_BACK_LABEL)),
		)
	}

	private fun showQuests() {
		debugPage = DebugPage.QUESTS
		debugChoices?.open(Quests.ALL.map { T(it.label) } + T(DEBUG_BACK_LABEL))
	}

	private fun showActions(quest: Quest) {
		debugPage = DebugPage.ACTIONS
		debugQuest = quest
		debugChoices?.open(listOf(T(ACTION_RESET_LABEL), T(ACTION_NEXT_LABEL), T(ACTION_FINISH_LABEL), T(DEBUG_BACK_LABEL)))
	}

	/** Remplit le sac d'un peu de tout, et donne deux objets rares pour voir leur présentation. */
	private fun fillBag() {
		Items.ALL.filter { !it.isKey }.forEachIndexed { index, item -> Inventory.add(item.id, index + 3) }
		close()
		MessageBox.instance?.play(
			listOf(
				N("Des objets de test ont été ajoutés au sac."),
				"@give:old_rod " + N("Vous recevez la Vieille canne !"),
				"@give:town_map " + N("Vous recevez la Carte du village !"),
			),
		)
	}

	/**
	 * Fait avancer une quête d'une étape, ou jusqu'au bout : ses drapeaux sont
	 * posés, le sac mis à jour, et la carte se recharge une fois le message
	 * refermé pour montrer ce que l'étape change.
	 */
	private fun advanceQuest(quest: Quest, all: Boolean) {
		val moved = if (all) quest.finish() else quest.advance()
		close()
		val message = when {
			!moved -> T(QUEST_ALREADY_DONE).format(T(quest.label))
			quest.isFinished -> "@reload " + T(QUEST_DONE).format(T(quest.label))
			else -> "@reload " + T(QUEST_STEP).format(T(quest.label))
		}
		MessageBox.instance?.play(listOf(message))
	}

	/**
	 * Fait repartir une quête de zéro : ses drapeaux sont retirés, le sac rendu
	 * à ce qu'il était, et la carte se recharge une fois le message refermé —
	 * chacun y reprend sa place d'avant. Si l'un d'eux revient là où se tient
	 * le joueur, celui-ci s'écarte d'une case (voir SceneManager.settlePlayer).
	 */
	private fun resetQuest(quest: Quest) {
		val undone = quest.reset()
		close()
		val message = if (undone) "@reload " + T(QUEST_RESET).format(T(quest.label)) else T(QUEST_NOT_STARTED).format(T(quest.label))
		MessageBox.instance?.play(listOf(message))
	}

	private fun placeCursor() {
		val entry = entries.getOrNull(selected) ?: return
		val list = entry.getParent() as? Control ?: return
		val arrow = cursor ?: return
		val y = list.getPosition().y + entry.getPosition().y + (entry.getSize().y - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}

private enum class DebugPage { TOOLS, QUESTS, ACTIONS }

private const val TOOL_BAG = 0
private const val TOOL_QUESTS = 1
private const val TOOL_TIME = 2
private const val TOOL_WEATHER = 3
private const val TOOL_DEX = 4
private const val ACTION_RESET = 0
private const val ACTION_NEXT = 1
private const val ACTION_FINISH = 2
private val DEBUG_BAG_LABEL = N("Remplir le sac")
private val DEBUG_QUESTS_LABEL = N("Quêtes")
private val DEBUG_DEX_LABEL = N("Pokédex national")
private val DEBUG_BACK_LABEL = N("Retour")
private val ACTION_RESET_LABEL = N("Repartir de zéro")
private val ACTION_NEXT_LABEL = N("Étape suivante")
private val ACTION_FINISH_LABEL = N("Finir la quête")
private val QUEST_STEP = N("« %s » : une étape de plus.")
private val QUEST_DONE = N("« %s » : la quête est terminée.")
private val QUEST_ALREADY_DONE = N("« %s » : la quête est déjà terminée.")
private val QUEST_RESET = N("« %s » : la quête repart de zéro.")
private val QUEST_NOT_STARTED = N("« %s » : la quête n'a pas encore commencé.")

private const val FRAMES_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/ui/frames/"
