shader_type canvas_item;

// Les nuages de l'écran titre : l'image défile à l'horizontale et se raccorde
// d'un bord à l'autre, sans fin.

// Vitesse, en largeurs d'image par seconde. Négative : vers la droite.
uniform float speed = 0.006;

// La teinte du nœud (son `modulate`), relevée avant que Godot n'y mêle la texture :
// dans `fragment`, COLOR contient déjà le pixel de l'image.
varying vec4 tint;

void vertex() {
	tint = COLOR;
}

void fragment() {
	COLOR = texture(TEXTURE, vec2(fract(UV.x + TIME * speed), UV.y)) * tint;
}
