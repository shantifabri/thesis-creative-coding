function setup() {
	createCanvas(500, 500);
	background(161, 205, 229); //red, green, blue (waterbottle blue)
	rectMode (CENTER); //changes rectangle origin
	
} //end of setup function

function draw() {
	fill(230, 70,100); // pink
	stroke(255); //white
	strokeWeight(3); //thikness of border
	//noStoke(); or noFill();//
	rect(250, 250, 200, 200); //x position, y position, width, height
	
	fill (130, 30, 150) //blue/purple for circle
	noStroke(); //no stroke for circle
	circle (250, 250, 150)
//put fill before shape//
	
} // end of draw function

