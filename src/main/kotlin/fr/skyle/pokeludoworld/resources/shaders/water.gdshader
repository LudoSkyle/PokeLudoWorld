shader_type canvas_item;

// L'eau qui bouge. Aucun des atlas n'a d'images d'animation pour l'eau : on la
// fait vivre ici, sans toucher au dessin des tuiles. Des rides claires, et
// quelques creux sombres, glissent en biais sur les pixels d'eau et sur eux
// seulement — le sable, la vase et les plantes d'une même tuile ne bougent pas.
//
// Le mouvement avance par crans, comme une animation image par image, et se
// compte en pixels du décor : une ride ne tombe jamais entre deux pixels.

// Nombre de crans par seconde.
uniform float steps_per_second = 4.0;
// Écart de couleur d'une ride, de 0 à 1.
uniform float strength = 0.06;

varying vec2 at;

void vertex() {
	// Position dans le calque, en pixels : les rides se suivent d'une tuile à l'autre.
	at = VERTEX;
}

void fragment() {
	vec4 texel = texture(TEXTURE, UV);
	// De l'eau : le bleu domine le rouge, et n'est pas dominé par le vert.
	float water = step(0.12, texel.b - texel.r) * step(texel.g * 0.9, texel.b);

	vec2 pixel = floor(at);
	float tick = floor(TIME * steps_per_second);

	// Des rides en biais, larges de deux ou trois pixels, qui glissent d'un pixel par cran...
	float ripple = sin((pixel.x + tick) * 0.3 + pixel.y * 0.62);
	// ...et une houle plus large, à contresens, qui les fait venir par bancs.
	float swell = sin((pixel.x - tick * 0.5) * 0.11 - pixel.y * 0.17);

	float crest = step(0.62, ripple) * step(-0.2, swell);
	float trough = step(ripple, -0.8) * step(swell, -0.2) * 0.5;
	float lift = crest - trough;

	COLOR.rgb += lift * strength * water;
}
