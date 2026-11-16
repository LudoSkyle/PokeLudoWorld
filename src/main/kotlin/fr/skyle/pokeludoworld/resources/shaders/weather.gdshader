shader_type canvas_item;
render_mode unshaded;

// La teinte d'écran de la météo, à la façon de RPG Maker (`Viewport#tone`,
// telle que Pokémon Essentials la règle pour chaque temps).
//
// Une teinte **ajoute** une couleur à l'image : la pluie retire 30 à chaque
// canal, la neige en ajoute 30, le sable ajoute du rouge et retire du bleu.
// Avant cela, elle peut lui retirer un peu de sa couleur (`tone_gray`).
// C'est la formule de mkxp, le moteur d'Essentials.
//
// Le rectangle qui porte ce shader couvre l'écran et relit ce qui a déjà été
// dessiné dessous — la carte, les personnages, la pluie.
//
// **La teinte de la météo passe SOUS celle de l'heure**, pas par-dessus. C'est
// le seul point où l'on s'écarte de RPG Maker, qui teinte l'image finale : de
// nuit, retirer 30 à une image déjà assombrie par l'heure la noyait — les deux
// teintes s'empilaient. Ici on défait d'abord la teinte de l'heure, on teinte
// le monde tel qu'il est en plein jour, puis on la remet : la pluie assombrit
// la nuit **en proportion**, comme elle assombrit le jour.

uniform sampler2D screen : hint_screen_texture, filter_nearest, repeat_disable;
/** Rouge, vert, bleu ajoutés à l'image, de -255 à 255. */
uniform vec3 tone_shift = vec3(0.0);
/** Ce qu'on lui retire de couleur, de 0 à 255. */
uniform float tone_gray = 0.0;

// La teinte de l'heure, que SceneManager règle à chaque image (voir daynight.md).
global uniform vec4 day_tint : source_color;

void fragment() {
	vec3 hour = max(day_tint.rgb, vec3(0.05));

	// Le monde tel qu'il serait en plein jour...
	vec3 color = texture(screen, SCREEN_UV).rgb / hour;
	// ...teinté par le temps qu'il fait...
	float luma = dot(color, vec3(0.299, 0.587, 0.114));
	color = mix(color, vec3(luma), tone_gray / 255.0);
	color = max(color + tone_shift / 255.0, vec3(0.0));
	// ...puis remis à l'heure. On ne borne qu'à la fin : la lumière d'un
	// lampadaire dépasse la teinte de la nuit, et doit le pouvoir.
	COLOR = vec4(clamp(color * hour, 0.0, 1.0), 1.0);
}
