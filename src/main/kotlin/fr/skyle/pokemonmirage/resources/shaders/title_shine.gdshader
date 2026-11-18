shader_type canvas_item;

// Un reflet qui traverse le logo de l'écran titre, de gauche à droite, à
// intervalles réguliers. Il éclaire les faces, pas les cernes sombres ; sur le
// blanc il ne se voit pas, c'est sur le bleu qu'on le suit.

// Secondes entre deux passages.
uniform float period = 5.0;
// Durée d'un passage, en secondes.
uniform float sweep = 0.9;
// Largeur du reflet, en fraction de la largeur de l'image.
uniform float width : hint_range(0.0, 0.5) = 0.07;
// Force du reflet.
uniform float strength : hint_range(0.0, 1.0) = 0.6;
// Pente du reflet : de combien il avance entre le haut et le bas de l'image.
uniform float slant = -0.12;

// La teinte du nœud (son `modulate`), relevée avant que Godot n'y mêle la texture :
// dans `fragment`, COLOR contient déjà le pixel de l'image.
varying vec4 tint;

void vertex() {
	tint = COLOR;
}

void fragment() {
	vec4 pixel = texture(TEXTURE, UV);
	float along = mod(TIME, period) / sweep;
	float centre = mix(-width - abs(slant), 1.0 + width + abs(slant), along);
	float distance_to = abs(UV.x + UV.y * slant - centre);
	float glow = smoothstep(width, 0.0, distance_to) * step(along, 1.0);
	// Tout sauf les cernes sombres : le reflet glisse sur les faces, pas sur les contours.
	float vivid = smoothstep(0.25, 0.55, dot(pixel.rgb, vec3(0.299, 0.587, 0.114)));
	pixel.rgb += vec3(glow * strength * vivid);
	COLOR = pixel * tint;
}
