#include "led-matrix.h"

#include <stdlib.h>
#include <unistd.h>
#include <list>

using rgb_matrix::GPIO;
using rgb_matrix::RGBMatrix;
using rgb_matrix::Canvas;
using std::list;

struct bodyPiece {
	int x, y;
};

void moveSnake(list<bodyPiece> *snake, int dx, int dy) {
	bodyPiece newhead;
	newhead.x = snake->front().x + dx;
	newhead.y = snake->front().y + dy;
	snake->push_front(newhead);
	snake->pop_back();
}

int checkHead(list<bodyPiece> *snake, int *board[32]) {
	if (snake->front().x < 0 or snake->front().y < 0
		or snake->front().x > 31 or snake->front().y > 31) {					// if snake is out of bounds
		return -1;
	}
	
	for (std::list<bodyPiece>::const_iterator i=snake->begin(); i!=snake->end(); ++i) {
		if ( i == snake->begin() ) {			// skip checking if the head is the head
			continue;
		}
		if (i->x == snake->front().x or i->y == snake->front().y ) {		// if any body piece is at the same coordinate as head
			return -1;
		}
	}
	if ( board[snake->front().y][snake->front().x] == 2 ) {			// if the snake is on top of an apple
		return 2;
	}
	return 0;
}

void placeApple(int *board[32]) {
	int x = 0;
    int y = 0;
    do {
        // Generate random x and y values within the map
        x = rand() % 2 + 30;
        y = rand() % 2 + 30;
        // If location is not free try again
    } while (board[y][x] != 0);

    // Place new food
    board[y][x] = 2;
}

static void draw(Canvas *canvas, int *board[32], int r, int g, int b) {
	canvas->Clear();
	for (int y=0; y<32; y++) {
		for (int x=0; x<32; x++) {
			switch(board[y][x]){
				case 0:
					break;
				case 1:
					canvas->SetPixel(x,y,r,g,b);
					break;
				case 2:
					canvas->SetPixel(x,y,255,0,0);
					break;
			}
		}
	usleep(1 * 1000);  // wait a little to slow down things.
	
	}
}

int main(int argc, char *argv[]) {
	
	GPIO io;
	if (!io.Init())
		return 1;
	int rows = 16;    // A 32x32 display. Use 16 when this is a 16x32 display.
	int chain = 1;    // Number of boards chained together.
	int parallel = 2; // Number of chains in parallel (1..3). > 1 for plus or Pi2
	
	Canvas *canvas = new RGBMatrix(&io, rows, chain, parallel);
	
	int[32][32] board = { 0 };		// 0 is empty space, 1 is snake body, 2 is apple
	int[32] *boardptr = &board;
	int dx, dy;
	
	list <bodyPiece> snake, *snakeptr;
	snakeptr = &snake;
	bodyPiece head;
	snake.push_front(head);
	bodyPiece pc2;
	bodyPiece pc3;
	
	// Game logic
	while(true) {
		
		canvas->Clear();

		// generate snake color
		int r = rand() % 256;
		int g = rand() % 256;
		int b = rand() % 256;
		
		// generate x and y starting position for new game
		snakeptr.front()->x = rand() % 2 + 30;
		snake.front()->y = rand() % 2 + 30;
		
		// add starting body pieces
		switch ( rand() % 4 ) {
			case 0:										// facing left
				pc2.x = [snake.front().x+1];
				pc2.y = [snake.front().y];
				pc3.x = [snake.front().x+2];
				pc3.y = [snake.front().y];
				dx = -1;
				dy = 0;
				break;
			case 1:										// facing down
				pc2.x = [snake.front().x];
				pc2.y = [snake.front().y-1];
				pc3.x = [snake.front().x];
				pc3.y = [snake.front().y-2];
				dx = 0;
				dy = 1;
				break;
			case 2:										// facing right
				pc2.x = [snake.front().x-1];
				pc2.y = [snake.front().y];
				pc3.x = [snake.front().x-2];
				pc3.y = [snake.front().y];
				dx = 1;
				dy = 0;
				break;
			case 3:										// facing up
				pc2.x = [snake.front().x];
				pc2.y = [snake.front().y+1];
				pc3.x = [snake.front().x];
				pc3.y = [snake.front().y+2];
				dx = 0;
				dy = -1;
				break;
				
		snake.push_back(pc2);
		snake.push_back(pc3);
		
		// insert snake onto blank board
		board[head.y][head.x] = 1;
		board[pc2.y][pc2.x] = 1;
		board[pc3.y][pc3.x] = 1;
		
		// place an apple
		placeApple(board);
		
		draw(canvas, boardptr, r, g, b);
		
		
		//draw
		
		while(true) {
			// is game over (out of bounds, etc)?
			// is apple eaten? place apple
			// determine location of apple, AI
			//set dx dy
			//move snake
			
			//draw(canvas, boardptr, r, g, b);
		}
		
		// snake deletion routine
		
		
	}
	
	canvas->Clear();
	
	delete canvas;

	return 0;
}