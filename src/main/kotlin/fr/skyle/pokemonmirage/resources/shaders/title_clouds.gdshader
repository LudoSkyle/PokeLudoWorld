shader_type canvas_item;

// Le temps du jeu, pas celui de la montre (GameClock.kt) : il remplace TIME.
global uniform float game_time;

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
	COLOR = texture(TEXTURE, vec2(fract(UV.x + game_time * speed), UV.y)) * tint;
}
