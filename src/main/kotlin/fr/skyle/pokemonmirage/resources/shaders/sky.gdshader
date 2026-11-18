shader_type canvas_item;

// Le voile du dehors : une brume claire sur toute la carte, et des bancs de
// nuages pâles qui dérivent lentement. Ils sont ancrés au monde — on marche
// dessous, ils ne suivent pas la caméra. Le tout par paliers et par grains de
// deux pixels, pour rester du pixel art.
//
// Posé par SceneManager sur toute carte d'extérieur (`metadata/daylight`), en
// un rectangle qui couvre la carte, au-dessus du décor et sous l'interface.

/** La couleur du voile : un blanc à peine bleuté. */
uniform vec3 tint : source_color = vec3(0.93, 0.97, 1.0);
/** L'opacité du voile là où il n'y a pas de nuage. */
uniform float haze : hint_range(0.0, 0.5) = 0.12;
/** Ce qu'un nuage ajoute, en son cœur. */
uniform float clouds : hint_range(0.0, 0.5) = 0.19;
/** La taille d'un nuage, en pixels. */
uniform float size = 170.0;
/** La dérive, en pixels par seconde. */
uniform vec2 drift = vec2(5.0, 1.5);
/** Le grain, en pixels. */
uniform float grain = 2.0;
/** Le nombre de paliers d'un nuage, du bord au cœur. */
uniform float levels = 4.0;

// La nuit, le voile se retire presque : c'est la nuit qui teinte.
global uniform float night_light;

varying vec2 world;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float value_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
	vec2 p = floor((world + drift * TIME) / grain) * grain / size;
	float n = 0.6 * value_noise(p) + 0.3 * value_noise(p * 2.1 + 7.3) + 0.1 * value_noise(p * 4.3 + 1.7);
	float cloud = floor(smoothstep(0.42, 0.72, n) * levels + 0.5) / levels;
	float alpha = (haze + clouds * cloud) * (1.0 - 0.8 * night_light);
	COLOR = vec4(tint, alpha);
}
