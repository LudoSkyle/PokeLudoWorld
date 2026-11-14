package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.ui.N
import godot.core.Color
import java.time.LocalTime

/**
 * Le cycle du jour et de la nuit, réglé sur **l'horloge réelle** de la
 * machine. Il a quatre moments — nuit, aube, jour, crépuscule — et passe de
 * l'un à l'autre progressivement, sans saut.
 *
 * Il ne fait que répondre à deux questions : quelle heure est-il, et de
 * quelle couleur cette heure teinte-t-elle le dehors. C'est SceneManager qui
 * applique la teinte aux cartes d'extérieur.
 */
object DayNight {

	/** Un moment de la journée : son nom, et une heure qui tombe en plein dedans. */
	enum class Moment(val label: String, val hour: Double, val tint: Color) {
		DAWN(N("Heure : aube"), 6.5, Color(0.96, 0.86, 0.92, 1.0)),
		DAY(N("Heure : jour"), 12.0, Color(1.0, 1.0, 1.0, 1.0)),
		DUSK(N("Heure : crépuscule"), 19.0, Color(1.0, 0.76, 0.58, 1.0)),
		NIGHT(N("Heure : nuit"), 23.0, Color(0.38, 0.44, 0.78, 1.0)),
	}

	/** Libellé de l'heure réelle, pour l'outil de mise au point. */
	val REAL = N("Heure : réelle")

	/**
	 * La journée, comme une suite de repères : à telle heure, telle teinte.
	 * Entre deux repères la teinte glisse de l'une à l'autre. Deux repères de
	 * même teinte font un palier.
	 */
	private val KEYS = listOf(
		0.0 to Moment.NIGHT,
		5.5 to Moment.NIGHT,
		6.5 to Moment.DAWN,
		7.5 to Moment.DAY,
		17.5 to Moment.DAY,
		19.0 to Moment.DUSK,
		20.5 to Moment.NIGHT,
		24.0 to Moment.NIGHT,
	)

	/**
	 * Heure imposée, de 0 à 24, ou null pour l'heure réelle. Sert à la mise au
	 * point : sans elle on ne verrait la nuit que la nuit.
	 */
	var forcedHour: Double? = null

	/** L'heure qu'il est, de 0 à 24 : 18,5 pour 18 h 30. */
	fun hour(): Double {
		forcedHour?.let { return it }
		val now = LocalTime.now()
		return now.hour + now.minute / 60.0 + now.second / 3600.0
	}

	/** La teinte du dehors à [hour]. Blanc : le décor est tel qu'il a été dessiné. */
	fun tint(hour: Double = hour()): Color {
		val time = ((hour % 24.0) + 24.0) % 24.0
		val next = KEYS.indexOfFirst { it.first > time }.takeIf { it > 0 } ?: (KEYS.size - 1)
		val (fromHour, from) = KEYS[next - 1]
		val (toHour, to) = KEYS[next]
		val progress = if (toHour > fromHour) (time - fromHour) / (toHour - fromHour) else 0.0
		return from.tint.lerp(to.tint, progress)
	}

	/** Le moment imposé en ce moment, ou null si l'on est à l'heure réelle. */
	val forcedMoment: Moment?
		get() = Moment.entries.firstOrNull { it.hour == forcedHour }

	/** Passe au moment suivant : réelle, aube, jour, crépuscule, nuit, puis de nouveau réelle. */
	fun cycle() {
		val moments = Moment.entries
		val current = forcedMoment
		forcedHour = when {
			current == null -> moments.first().hour
			current == moments.last() -> null
			else -> moments[current.ordinal + 1].hour
		}
	}

	/** Le libellé de l'heure en cours, pour l'outil de mise au point. */
	fun label(): String = forcedMoment?.label ?: REAL
}
