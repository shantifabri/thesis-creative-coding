function setup() {
	createCanvas(500,500);
	rectMode(CENTER);//changes rectangle origin
}//end of setup function

function draw() {
	background(255,255,0);
	square(250,250,300,10)
	fill(0,127,26);
	stroke(0);
	strokeWeight(3);
	circle(250,250,100)
	fill(26,0,127);
	stroke(0);
	strokeWeight(3);//thickness of border
	noStroke();//turn off stroke
	//noFill();//turn off fill
}//end of draw