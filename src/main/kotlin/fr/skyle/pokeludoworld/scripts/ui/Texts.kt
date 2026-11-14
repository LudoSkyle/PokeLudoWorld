package fr.skyle.pokeludoworld.scripts.ui

import godot.api.TranslationServer
import godot.core.asStringName

/**
 * Traduit un texte écrit en français dans la langue choisie. Sans traduction
 * (ou en français), le texte revient tel quel.
 *
 * Les `Label` des scènes se traduisent seuls. Cette fonction sert aux textes
 * fabriqués par le code : boîte de dialogue, phrases à trous.
 * Tout texte passé ici doit avoir son entrée dans `locale/en.po` — c'est
 * vérifié par `tests/run.sh i18n`.
 */
/**
 * Marque un texte français qui sera traduit plus tard, à l'affichage : le nom
 * d'un objet, le titre d'une poche. Ne fait rien, sinon le signaler à
 * `tests/run.sh i18n`.
 */
fun N(text: String): String = text

fun T(text: String): String = TranslationServer.translate(text.asStringName()).toString()
