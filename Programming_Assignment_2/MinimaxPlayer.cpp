/*
 * MinimaxPlayer.cpp
 *
 *  Created on: Apr 17, 2015
 *     Authors: wong, Mark Bereza
 */
#include <iostream>
#include <assert.h>
#include <climits>      // For INT_MAX and INT_MIN
#include <utility>
#include "MinimaxPlayer.h"

using namespace std;

MinimaxPlayer::MinimaxPlayer(char symb) :
		Player(symb) {

}

MinimaxPlayer::~MinimaxPlayer() {

}

/* A structure representing a game state. */
struct state {
    OthelloBoard* board;    /* Current board state. */
    char symbol;            /* Symbol for the current player. */
};

/**
 * @param   s   The game state to be linearized.
 * @return      The string representation of that game state.
 *
 * Creates a string representation of a given game state (board state + current player). This string
 * is useful because unordered_map has a builtin hashing function for strings, meaning it can be
 * used as a unique key for any given game state.
 */
string linearize(state s) {
    string hash = "";
    for (int c = 0; c < s.board->get_num_cols(); c++)
        for (int r = 0; r < s.board->get_num_rows(); r++)
            hash += s.board->get_cell(c, r);
    hash += s.symbol;
    return hash;
}

/**
 * @param   b   The board state on which to apply the terminal test.
 * @return      A boolean representing whether or not the given board state is a terminal one.
 *
 * Determines whether or not the provided board state is terminal by checking if either player can
 * still move.
 */
bool terminal_test(OthelloBoard* b) {
    return !(b->has_legal_moves_remaining('X') || b->has_legal_moves_remaining('O'));
}

/**
 * @param   b   The board state to evaluate the utility of.
 * @return      An integer value representing the utility.
 *
 * The utility of a terminal state can be calculated simply by subtracting the second player's score
 * from the first player's score. This is because we are told that the first player is the
 * maximizing player, so they should be trying to win by as many points as possible. If the first
 * player cannot win, they should be trying to lose by as few points as possible. Naturally, the
 * opposite is true for the second (minimizing) player.
 */
int utility(OthelloBoard* b) {
    return (b->count_score(b->get_p1_symbol()) - b->count_score(b->get_p2_symbol()));
}

/**
 * @param   s       The current game state.
 * @param   lookup  A reference to the state->move lookup table being generated.
 * @return          The utility of the "best move" for the current node in the game tree.
 *
 * This method recursively generates the game tree and uses the minimax algorithm to determine the
 * best move for each node in that tree. The best moves are then stored in a lookup table
 * (implemented using a hash map) that associates game states with the best move for that game
 * state. A "move" (action) is encoded as a pair of ints: the row and column of the move to be made.
 */
int build_lookup(state s, action_map& lookup) {
    int best_util;      // The best utility for this state.
    bool max;           // True if we're trying to maximize utility; false otherwise.
    char other_symbol;

    // Since ints can't be infinity, we settle for INT_MIN or INT_MAX, as appropriate.
    if (s.symbol == s.board->get_p1_symbol()) {
        best_util = INT_MIN;
        max = true;
        other_symbol = s.board->get_p2_symbol();
    } else {
        best_util = INT_MAX;
        max = false;
        other_symbol = s.board->get_p1_symbol();
    }

    // If the current state is terminal, the utility is determined using the utility functioon.
    if (terminal_test(s.board)) {
        best_util = utility(s.board);
    } 
    
    // If the current player cannot move but the opposing player can, the current player passes.
    else if (!s.board->has_legal_moves_remaining(s.symbol) && 
              s.board->has_legal_moves_remaining(other_symbol)) {
        state child;
        child.board = new OthelloBoard(*(s.board));
        child.symbol = other_symbol;
        best_util = build_lookup(child, lookup);
        delete child.board;
    } 
    
    // If the current player can move, then we recursively call build_lookup() on all successors.
    else {
        action best_move;
        int cur_util;
        for (int c = 0; c < s.board->get_num_cols(); c++) {
            for (int r = 0; r < s.board->get_num_rows(); r++) {
                if (s.board->is_cell_empty(c, r) && s.board->is_legal_move(c, r, s.symbol)) {
                    state child;
                    child.board = new OthelloBoard(*(s.board));
                    child.board->play_move(c, r, s.symbol);
                    child.symbol = other_symbol;
                    cur_util = build_lookup(child, lookup);
                    if ((max && (cur_util > best_util)) || (!max && (cur_util < best_util))) {
                        best_move = make_pair(c, r);
                        best_util = cur_util;
                    }
                    delete child.board;
                }
            }
        }
        lookup[linearize(s)] = best_move;   // Add the best move to the lookup table.
    }

    return best_util;
}

void MinimaxPlayer::get_move(OthelloBoard* b, int& col, int& row) {
    // Construct the current game state.
    state s;
    s.board = b;
    s.symbol = symbol;

    // Lookup table is created using lazy initialization.
    if (lookup.empty())
        build_lookup(s, lookup);

    // Lookup the best move.
    auto move = lookup[linearize(s)];
    col = move.first;
    row = move.second;
}

MinimaxPlayer* MinimaxPlayer::clone() {
	MinimaxPlayer* result = new MinimaxPlayer(symbol);
	return result;
}
