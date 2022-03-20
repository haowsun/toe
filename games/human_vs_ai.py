import functools
import collections
import os
import random
import numpy as np
import tensorflow as tf

from games.tic_tac_toe import TicTacToeGameSpec, human_player
from common.network_helpers import load_network, get_stochastic_network_move,create_network

def human_vs_ai() :
    NETWORK_FILE_PATH ='current_network.p' #保存数据的位置
    RANDOMIZE_FIRST_PLAYER=True     #是否随机先手

    game_spec = TicTacToeGameSpec()
    create_network_func = functools.partial(create_network, game_spec.board_squares(), (100, 100, 100))

    input_layer, output_layer, variables = create_network_func()

    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        if NETWORK_FILE_PATH and os.path.isfile(NETWORK_FILE_PATH):
            print("loading pre-existing network")
            load_network(session, variables, NETWORK_FILE_PATH)

        mini_batch_board_states, mini_batch_moves = [], []

        def make_training_move(board_state, side):
            mini_batch_board_states.append(np.ravel(board_state) * side)
            move = get_stochastic_network_move(session, input_layer, output_layer, board_state, side)
            mini_batch_moves.append(move)
            return game_spec.flat_move_to_tuple(move.argmax())
        
        if (not RANDOMIZE_FIRST_PLAYER) or bool(random.getrandbits(1)):
            game_spec.play_game(make_training_move, human_player,log=False)
        else:
            game_spec.play_game(human_player, make_training_move,log=False)

if __name__ == '__main__':
    # example of playing a game
    human_vs_ai()