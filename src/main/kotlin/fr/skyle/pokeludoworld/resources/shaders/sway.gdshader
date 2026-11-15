shader_type canvas_item;

// Le vent dans les plantes. Aucun des atlas n'a d'images d'animation pour la
// végétation : on la fait bouger ici, sans toucher au dessin des tuiles. Le
// pied reste planté, la cime se décale d'un pixel ou deux, de plus en plus en
// montant.
//
// Comme l'eau, le mouvement avance par crans et se compte en pixels du décor :
// une feuille ne tombe jamais entre deux pixels.

// Nombre de crans par seconde.
uniform float steps_per_second = 3.0;
// Décalage de la cime, en pixels.
uniform float reach = 1.0;
// Hauteur du bas de cette tuile dans la plante, en tuiles : 0 pour le pied,
// 1 pour la cime d'une plante de deux cases de haut.
uniform float base = 0.0;
// Taille de la tuile, en pixels.
uniform vec2 tile = vec2(16.0, 16.0);
// Coin haut-gauche de la tuile dans l'atlas, en pixels. Négatif : la tuile
// fait partie d'une grille de `tile` pixels à marge de 1, on retrouve sa
// place tout seul.
uniform vec2 origin = vec2(-1.0, -1.0);

varying vec2 at;

void vertex() {
	// Position dans le calque, en pixels : chaque plante a son propre rythme.
	at = VERTEX;
}

void fragment() {
	vec2 pixel = UV / TEXTURE_PIXEL_SIZE;
	vec2 local = origin.x < 0.0 ? mod(pixel - vec2(1.0), tile) : pixel - origin;

	// 0 au pied de la plante, 1 en haut de sa première tuile, 2 en haut de sa cime.
	float height = (tile.y - local.y) / 16.0 + base;
	vec2 plant = floor(at / 16.0) + vec2(0.0, base);
	float tick = floor(TIME * steps_per_second);
	float wind = sin(tick * 0.8 + plant.x * 1.7 + plant.y * 0.6) + 0.5 * sin(tick * 0.31 + plant.x * 0.4);

	float shift = round(wind * reach * 0.34 * height);
	float x = local.x - shift;

	// Un pixel qui irait chercher son dessin hors de la tuile reste à sa place :
	// sans ça, une plante aussi large que sa case se troue sur un bord à chaque
	// coup de vent — et irait lire la tuile voisine de l'atlas.
	if (x < 0.0 || x >= tile.x) {
		shift = 0.0;
	}
	COLOR = texture(TEXTURE, UV - vec2(shift, 0.0) * TEXTURE_PIXEL_SIZE);
}
