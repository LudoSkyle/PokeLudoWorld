shader_type canvas_item;

// Les fenêtres qui s'allument la nuit. Posé sur les tuiles de maison qui ont
// une vitre : leurs pixels bleu vitre, et eux seuls, virent au jaune chaud à
// mesure que la nuit tombe. Le dessin des tuiles n'est pas modifié.
//
// La nuit teinte tout le dehors (voir DayNight) ; une fenêtre éclairée ne doit
// pas l'être. On divise donc sa couleur par la teinte du moment, que le moteur
// remultiplie ensuite : il reste la lumière telle quelle.

// Force des lumières, de 0 (jour) à 1 (nuit). Réglée par SceneManager.
global uniform float night_light;
// Teinte du dehors en ce moment. Réglée par SceneManager.
global uniform vec4 day_tint : source_color;

// Couleur d'une vitre éclairée.
uniform vec3 lit : source_color = vec3(1.0, 0.86, 0.45);

void fragment() {
	vec4 texel = texture(TEXTURE, UV);
	// Une vitre : bleu clair, le bleu dominant nettement le rouge.
	float glass = step(0.7, texel.b) * step(0.2, texel.b - texel.r) * step(0.45, texel.g);

	// Les reflets de la vitre restent plus clairs que le reste.
	float shine = 0.82 + 0.18 * smoothstep(0.55, 0.95, texel.r);
	vec3 lamp = lit * shine / max(day_tint.rgb, vec3(0.05));

	COLOR.rgb = mix(COLOR.rgb, lamp, glass * night_light);
}
