########################################################################################################################
# Import required libraries
from copy import deepcopy
import random
import time
import sys

###########################################################
# Function to return the enemy's colour
# Returns the color of the enemy as 'b' or 'w' (black or white) depending on board value (color here refers to board[x][y])
def enemys_color(color):
    if (color.upper() == 'B'):
        return 'w'
    elif (color.upper() == 'W'):
        return 'b'
    else:
        return '.'

###########################################################
# Function to return the board's grid position (0,0)~(7,7) given the board's serial position from 1-32
def serial_position_to_grid_position(serial_position):
    return (
    (int(serial_position) - 1) // 4, 2 * ((int(serial_position) - 1) % 4) + 1 - ((int(serial_position) - 1) // 4) % 2)

###########################################################
# Function to return the board's serial position 1-32 given the board's grid position (0,0)~(7,7)
def grid_position_to_serial_position(x, y):
    return 4 * x + y // 2 + 1

###########################################################
# Function to check whether the move from (x1,y1) to (x2,y2) (either a single move or a capture) can be performed or not
def go_from_position_to_position_allowed_or_not(board, x1, y1, x2, y2):
    # boundary constraints ( (0,0)~(7,7) )
    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > 7 or y1 > 7 or x2 > 7 or y2 > 7:
        return False

    color = board[x1][y1]

    # check whether the current position is empty
    if color == '.':
        return False

    # check whether the destination position is not empty
    if board[x2][y2] != '.':
        return False

    x_coord_diff = abs(x1 - x2)
    y_coord_diff = abs(y1 - y2)

    # check whether the x coordinates' difference is >2 (only single diagonal move with diff 1 or capture(max one opponent piece in b/w) with diff 2 is allowed)
    if x_coord_diff != 1 and x_coord_diff != 2:
        return False

    # check whether proper diagonal move
    if x_coord_diff != y_coord_diff:
        return False

    # if it's a white man, it cannot move backwards, so x2 has to be < x1
    if color == 'w' and x2 > x1:
        return False

    # if it's a black man, it cannot move backwards, so x2 has to be > x1
    if color == 'b' and x2 < x1:
        return False

    # if there's a possibility of a capture move, check whether the piece that is being crossed over is an enemy piece or not (the middle piece must be the enemy's in order for it to be captured)
    if x_coord_diff == 2:
        if board[int((x1 + x2) / 2)][int((y1 + y2) / 2)].lower() != enemys_color(color):
            return False

    return True

###########################################################
# Function to check whether a piece can be captured or not from the position (x,y)
def jump_possible_or_not_from_position(board, x, y):
    # Check whether a jump is possible in any of the four directions
    if go_from_position_to_position_allowed_or_not(board, x, y, x + 2, y + 2) == True:
        return True
    if go_from_position_to_position_allowed_or_not(board, x, y, x + 2, y - 2) == True:
        return True
    if go_from_position_to_position_allowed_or_not(board, x, y, x - 2, y - 2) == True:
        return True
    if go_from_position_to_position_allowed_or_not(board, x, y, x - 2, y + 2) == True:
        return True

    return False

###########################################################
# Function to check whether a piece can be captured or not from the position (x,y) by one of our pieces
def jump_possible_or_not_by_us(board, color):
    # iterate over all board positions
    for piece in range(1, 33):
        p = serial_position_to_grid_position(piece)
        x = p[0]
        y = p[1]

        # Check whether this board position is our color
        if board[x][y].upper() == color.upper():
            if jump_possible_or_not_from_position(board, x, y) == True:
                return True

    return False

###########################################################
# Function to move from (x1,y1) to (x2,y2) on the board and alter it (simple move or a capture (but not multiple capture))
# Returns whether any capture has been made and also the new board after the move has been performed
def move_from_to_position(board, x1, y1, x2, y2):
    has_been_captured = False

    board[x2][y2] = board[x1][y1]
    board[x1][y1] = '.'

    if abs(x1 - x2) == 2:  # It's a capture move
        board[int((x1 + x2) / 2)][int((y1 + y2) / 2)] = '.'
        has_been_captured = True

    if x2 == 0 or x2 == 7:
        # make our piece a king, even if it already is a king
        board[x2][y2] = board[x2][y2].upper()

    return has_been_captured, board

###########################################################
# Function to perform all moves from the move list
def perform_all_moves(board, move):
    # get the starting position of the move
    p = serial_position_to_grid_position(move[0])
    x1 = p[0]
    y1 = p[1]

    # iterate over the second to the last items on the move list
    for i in range(1, len(move)):
        p = serial_position_to_grid_position(move[i])
        x2 = p[0]
        y2 = p[1]

        # do the move
        has_been_captured, board_after_move = move_from_to_position(board, x1, y1, x2, y2)

        # next loop
        x1 = x2
        y1 = y2

    return board_after_move

###########################################################
# Function to check whether the move performed by us will be legal or not
def move_legal_or_not(board, move, color):
    # if the move only contains one element i.e. the starting position, then no legal move exists
    if len(move) < 2:
        return False

    # get the starting position of the move
    p = serial_position_to_grid_position(move[0])
    x1 = p[0]
    y1 = p[1]

    # checks whether the starting position value is same as the current position value
    if board[x1][y1].lower() != color.lower():
        return False

    # checks whether a capture is possible, if possible the player must capture
    has_been_captured_move = jump_possible_or_not_by_us(board, color)

    # if there's no capture move possible, there should only be 2 elements in the move
    if has_been_captured_move == False and len(move) != 2:
        return False

    # temporary board
    temp_board = deepcopy(board)

    # iterate over the second to the last items on the move list
    for i in range(1, len(move)):
        p = serial_position_to_grid_position(move[i])
        x2 = p[0]
        y2 = p[1]

        if go_from_position_to_position_allowed_or_not(temp_board, x1, y1, x2, y2) == False:
            return False

        # do the move
        has_been_captured, board_after_move = move_from_to_position(temp_board, x1, y1, x2, y2)
        if has_been_captured_move != has_been_captured:
            return False

        # next loop
        x1 = x2
        y1 = y2

    # check whether the jump is complete and whether any other jump can be made from the last position
    if has_been_captured_move == True:
        if jump_possible_or_not_from_position(temp_board, x1, y1) == True:  # now (x1,y1)=(x2,y2)
            return True  # since we are allowed multiple subsequent captures

    return True

###########################################################
# Function to check whether any valid move (single move or capture) can be performed by us or not
def any_valid_move_possible_or_not(board, color):
    # iterate over all board positions
    for piece in range(1, 33):
        p = serial_position_to_grid_position(piece)
        x = p[0]
        y = p[1]

        # for single move
        # check whether this board position is our color
        if board[x][y].upper() == color.upper():
            if go_from_position_to_position_allowed_or_not(board, x, y, x + 1, y - 1) == True:
                # we can move to bottom left
                return True

            if go_from_position_to_position_allowed_or_not(board, x, y, x + 1, y + 1) == True:
                # we can move to bottom right
                return True

            if go_from_position_to_position_allowed_or_not(board, x, y, x - 1, y - 1) == True:
                # we can move to top left
                return True

            if go_from_position_to_position_allowed_or_not(board, x, y, x - 1, y + 1) == True:
                # we can move to top right
                return True

    # for jump
    if jump_possible_or_not_by_us(board, color) == True:
        return True

    return False

###########################################################
# Function to return all the possible jump moves from (x,y)
def all_jump_moves_from_position(board, x, y):
    moves = []
    serial_position = grid_position_to_serial_position(x, y)

    for i in [-2, 2]:
        for j in [-2, 2]:
            # check in all four directions
            if go_from_position_to_position_allowed_or_not(board, x, y, x + i, y + j):
                temp_board = deepcopy(board)
                move_from_to_position(temp_board, x, y, x + i, y + j)
                child_jump_moves = all_jump_moves_from_position(temp_board, x + i, y + j)

                if len(child_jump_moves) == 0:
                    moves.append([serial_position, grid_position_to_serial_position(x + i, y + j)])
                else:
                    for cjm in child_jump_moves:
                        sp = [serial_position]
                        sp.extend(cjm)
                        moves.append(sp)

    return moves

###########################################################
# Function to return all the possible moves from (x,y)
def all_possible_moves_from_position(board, x, y):
    moves = []
    has_been_captured = False

    # check for jumps
    jm = all_jump_moves_from_position(board, x, y)
    for m in jm:
        moves.append(m)

    if len(moves) == 0:  # i.e if no jump moves are available
        # check for single moves
        serial_position = grid_position_to_serial_position(x, y)

        if go_from_position_to_position_allowed_or_not(board, x, y, x + 1, y - 1):
            moves.append([serial_position, grid_position_to_serial_position(x + 1, y - 1)])
        if go_from_position_to_position_allowed_or_not(board, x, y, x + 1, y + 1):
            moves.append([serial_position, grid_position_to_serial_position(x + 1, y + 1)])
        if go_from_position_to_position_allowed_or_not(board, x, y, x - 1, y - 1):
            moves.append([serial_position, grid_position_to_serial_position(x - 1, y - 1)])
        if go_from_position_to_position_allowed_or_not(board, x, y, x - 1, y + 1):
            moves.append([serial_position, grid_position_to_serial_position(x - 1, y + 1)])

    else:
        has_been_captured = True

    return moves, has_been_captured  # so, if there are jump moves available, we will always select a jump move over a single move


###########################################################
# Function to return all the possible moves by our pieces
def all_possible_moves_by_us(board, color):
    moves = []
    capture_possible_by_us = jump_possible_or_not_by_us(board, color)

    # iterate over all board positions
    for piece in range(1, 33):
        p = serial_position_to_grid_position(piece)
        x = p[0]
        y = p[1]

        # check whether this board position is our color
        if board[x][y].upper() == color.upper():

            apm, has_been_captured = all_possible_moves_from_position(board, x, y)

            if capture_possible_by_us == has_been_captured:
                for m in apm:
                    moves.append(m)
    return moves

###########################################################
# Evaluation function (Minimax)
# Values at the leaf nodes are calculated first and then keep getting calculated at each level up
def evaluation(board, color, depth, whose_chance_to_play, enemy_color, alpha, beta):
    if depth > 1:  # comes here (depth-1) times and goes to else for leaf nodes
        depth -= 1
        opti = float(
            "-inf")  # opti will contain the best value for player in MAX chance and worst value for player in MIN chance

        # us
        if whose_chance_to_play == 'max':
            moves = all_possible_moves_by_us(board, color)  # we get all of our possible moves
            random.shuffle(moves)

            for move in moves:
                next_board = deepcopy(board)
                perform_all_moves(next_board, move)
                if beta > opti:
                    value = evaluation(next_board, color, depth, 'min', enemy_color, alpha, beta)
                    if value > opti:  # -inf is less than everything and anything so we don't need opti == -inf check
                        opti = value
                    if opti > alpha:
                        alpha = opti

        # enemy
        elif whose_chance_to_play == 'min':
            moves = all_possible_moves_by_us(board, enemy_color)  # we get all of our enemy's possible moves
            random.shuffle(moves)

            for move in moves:
                next_board = deepcopy(board)
                perform_all_moves(next_board, move)
                if alpha == float("-inf") or opti == float(
                        "-inf") or alpha < opti:  # -inf conditions are to be checked only for the first time
                    value = evaluation(next_board, color, depth, 'max', enemy_color, alpha, beta)
                    if opti == float("-inf") or value < opti:  # opti = -inf for the first time
                        opti = value
                    if opti < beta:
                        beta = opti

        return opti

    else:  # comes here for the last level i.e for leaf nodes
        value = 0

        # iterate over all board positions
        for piece in range(1, 33):
            p = serial_position_to_grid_position(piece)
            x = p[0]
            y = p[1]

            # heuristic
            if board[x][y] == color.lower():  # our man
                if color.lower() == 'b':
                    if x > 3:
                        value += 7
                    else:
                        value += 5

                if color.lower() == 'w':
                    if x < 4:
                        value += 7
                    else:
                        value += 5

            elif board[x][y] == color.upper():  # our king
                value += 10 + abs(x-3)

            elif board[x][y] == enemy_color.lower():  # enemy's man
                if enemy_color.lower() == 'b':
                    if x > 3:
                        value -= 7
                    else:
                        value -= 5

                if enemy_color.lower() == 'w':
                    if x < 4:
                        value -= 7
                    else:
                        value -= 5

            elif board[x][y] == enemy_color.upper():  # enemy's king
                value -= 10 - abs(x-3)

        return value

###########################################################
# Function to return our best move depending on the time remaining to play our game
def next_move(board, color, time_remaining):
    moves = all_possible_moves_by_us(board, color)

    # if only one move is possible, return that
    if len(moves) == 1:
        return moves[0]

    # get the enemy's color
    enemy_color = enemys_color(color)

    equal_moves = []  # equal_moves consists of all the moves that end up with the same value after the Minimax evaluation

    best = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    if time_remaining < 1:
        depth = 2
    else:
        depth = 5

    for move in moves:  # this is MAX's chance (1st level of minimax), so next should be MIN's chance
        new_board = deepcopy(board)
        perform_all_moves(new_board, move)

        # beta is always inf here as there is no parent MIN node, so no need to check if we can prune or not
        move_val = evaluation(new_board, color, depth, 'min', enemy_color, alpha, beta)
        if best == float("-inf") or move_val > best:
            best_move = move
            best = move_val

            equal_moves = []
            equal_moves.append(move)
        elif move_val == best:
            equal_moves.append(move)
        if best > alpha:
            alpha = best

    # This tries to check whether there is any next move that will form a defensive structure from the
    # equal_moves list and returns it.
    if len(equal_moves) > 1:
        for move in equal_moves:
            l = len(move)

            p = serial_position_to_grid_position(move[l - 1])
            x = p[0]
            y = p[1]

            if (x + 1) <= 7:
                if (y + 1) <= 7 and board[x + 1][y + 1].lower() == color.lower():
                    return move
                if (y - 1) >= 0 and board[x + 1][y - 1].lower() == color.lower():
                    return move
            if (x - 1) >= 0:
                if (y + 1) <= 7 and board[x - 1][y + 1].lower() == color.lower():
                    return move
                if (y - 1) >= 0 and board[x - 1][y - 1].lower() == color.lower():
                    return move

    return best_move

###########################################################
# Function for 'single' mode
# Returns any possible valid move (jump over single move)
def play_single():
    if color_play == 'BLACK':
        color = 'b'
    else:
        color = 'w'

    while any_valid_move_possible_or_not(board, color) == True:
        temp_board = deepcopy(board)
        moves = all_possible_moves_by_us(temp_board, color)

        if len(moves) == 1:
            move_final = []
            move = moves[0]
            if move_legal_or_not(board, move, color) == True:
                for position in move:
                    position = serial_position_to_grid_position(position)
                    move_final.append(position)

            return move_final

        moves_final = []
        for move in moves:
            move_final = []
            if move_legal_or_not(board, move, color) == True:
                for position in move:
                    position = serial_position_to_grid_position(position)
                    move_final.append(position)
                moves_final.append(move_final)

        moves_final_jumps = []
        moves_final_single_moves = []

        for i in range(0, len(moves_final)):
            x1 = moves_final[i][0][0]
            y1 = moves_final[i][0][1]

            x2 = moves_final[i][1][0]
            y2 = moves_final[i][1][1]

            # check whether the move is a jump or not
            if (abs(x1 - x2) == 2 and abs(y1 - y2) == 2):
                moves_final_jumps.append(moves_final[i])
            else:
                moves_final_single_moves.append(moves_final[i])

        # if a jump is possible, we will always return that over a single move
        if len(moves_final_jumps) != 0:
            random_number = random.randint(0, len(moves_final_jumps) - 1)
            # to return a random jump out of all the jumps possible
            return moves_final_jumps[random_number]
        else:
            random_number = random.randint(0, len(moves_final) - 1)
            # else return a random move out of all the moves possible
            return moves_final[random_number]

###########################################################
# Function for 'game' mode
# Returns the best possible valid move
def play_game():
    if color_play == 'BLACK':
        color = 'b'
    else:
        color = 'w'

    while any_valid_move_possible_or_not(board, color) == True:
        temp_board = deepcopy(board)
        next_move_to_be_returned = next_move(temp_board, color, time_remaining)

        if move_legal_or_not(board, next_move_to_be_returned, color) == True:
            perform_all_moves(board, next_move_to_be_returned)

            return next_move_to_be_returned, board

###########################################################
# read input
# make all important variables global
global game_type, color_play, time_remaining, board1, board

input_file = open("input.txt")
input_file_string = input_file.read().split('\n')

game_type = input_file_string[0]
color_play = input_file_string[1]
time_remaining = float(input_file_string[2])

board1 = []

for i in range(8):
    a = input_file_string[3 + i]
    board1.append(a)

board = [list(split) for split in board1]

# Play
fp = open("output.txt", "w")

notations = {"0": "a", "1": "b", "2": "c", "3": "d", "4": "e", "5": "f", "6": "g", "7": "h"}

# for 'single' mode
if game_type == 'SINGLE':
    result = play_single()

    # for single/multiple jumps
    x1 = result[0][0]
    y1 = result[0][1]

    x2 = result[1][0]
    y2 = result[1][1]

    if (abs(x1 - x2) == 2 and abs(y1 - y2) == 2):
        output_final_jumps = []

        for i in range(0, len(result) - 1):
            x1 = result[i][0]
            y1 = result[i][1]

            letter_jumps = notations["{0}".format(y1)]
            output_jumps = "J" + " " + letter_jumps + "{0}".format(8 - x1)

            output_final_jumps.append(output_jumps)

        letter_last_position_jumps = notations["{0}".format(result[len(result) - 1][1])]
        output_last_position_jumps = "J" + " " + letter_last_position_jumps + "{0}".format(
            8 - result[len(result) - 1][0])
        output_final_jumps.append(output_last_position_jumps)

        output_final_jumps_final = []
        output_final_jumps_final.append(output_final_jumps[0])

        # if our piece becomes a king during one of the moves, we have to stop
        i = 1
        while i < (len(output_final_jumps)):
            if color_play == 'BLACK':
                char_to_be_checked = '1'
                if output_final_jumps[i][3] == char_to_be_checked:
                    output_final_jumps_final.append(output_final_jumps[i])
                    break
                else:
                    output_final_jumps_final.append(output_final_jumps[i])


            elif color_play == 'WHITE':
                char_to_be_checked = '8'
                if output_final_jumps[i][3] == char_to_be_checked:
                    output_final_jumps_final.append(output_final_jumps[i])
                    break
                else:
                    output_final_jumps_final.append(output_final_jumps[i])

            i += 1

        for i in range(0, len(output_final_jumps_final) - 1):
            output_to_be_written_to_file_jumps = output_final_jumps_final[i] + " " + output_final_jumps_final[
                i + 1].replace("J", "").replace(" ", "")
            print(output_to_be_written_to_file_jumps, '\n', end="", file=fp)

    # for single move
    else:
        output_final_move = []

        x1 = result[0][0]
        y1 = result[0][1]

        x2 = result[1][0]
        y2 = result[1][1]

        letter_move = notations["{0}".format(y1)]
        output_move = "E" + " " + letter_move + "{0}".format(8 - x1)
        output_final_move.append(output_move)

        letter_last_position_move = notations["{0}".format(y2)]
        output_last_position_move = "E" + " " + letter_last_position_move + "{0}".format(8 - x2)

        output_final_move.append(output_last_position_move)

        output_to_be_written_to_file_move = output_final_move[0] + " " + output_final_move[1].replace("E",
                                                                                                      "").replace(
            " ", "")
        print(output_to_be_written_to_file_move, end="", file=fp)

# for 'game' mode
if game_type == 'GAME':
    serial_result, final_board_after_move = play_game()

    for row in final_board_after_move:
        for element in row:
            sys.stdout.write(element[0])
        sys.stdout.write('\n')

    result = []
    for position in serial_result:
        position = serial_position_to_grid_position(position)
        result.append(position)

    # for single/multiple jumps
    x1 = result[0][0]
    y1 = result[0][1]

    x2 = result[1][0]
    y2 = result[1][1]

    if (abs(x1 - x2) == 2 and abs(y1 - y2) == 2):
        output_final_jumps = []

        for i in range(0, len(result) - 1):
            x1 = result[i][0]
            y1 = result[i][1]

            letter_jumps = notations["{0}".format(y1)]
            output_jumps = "J" + " " + letter_jumps + "{0}".format(8 - x1)

            output_final_jumps.append(output_jumps)

        letter_last_position_jumps = notations["{0}".format(result[len(result) - 1][1])]
        output_last_position_jumps = "J" + " " + letter_last_position_jumps + "{0}".format(
            8 - result[len(result) - 1][0])
        output_final_jumps.append(output_last_position_jumps)

        output_final_jumps_final = []
        output_final_jumps_final.append(output_final_jumps[0])

        # if our piece becomes a king during one of the moves, we have to stop
        i = 1
        while i < (len(output_final_jumps)):
            if color_play == 'BLACK':
                char_to_be_checked = '1'
                if output_final_jumps[i][3] == char_to_be_checked:
                    output_final_jumps_final.append(output_final_jumps[i])
                    break
                else:
                    output_final_jumps_final.append(output_final_jumps[i])

            elif color_play == 'WHITE':
                char_to_be_checked = '8'
                if output_final_jumps[i][3] == char_to_be_checked:
                    output_final_jumps_final.append(output_final_jumps[i])
                    break
                else:
                    output_final_jumps_final.append(output_final_jumps[i])

            i += 1

        for i in range(0, len(output_final_jumps_final) - 1):
            output_to_be_written_to_file_jumps = output_final_jumps_final[i] + " " + output_final_jumps_final[
                i + 1].replace("J", "").replace(" ", "")
            print(output_to_be_written_to_file_jumps, '\n', end="", file=fp)

    # for single move
    else:
        output_final_move = []

        x1 = result[0][0]
        y1 = result[0][1]

        x2 = result[1][0]
        y2 = result[1][1]

        letter_move = notations["{0}".format(y1)]
        output_move = "E" + " " + letter_move + "{0}".format(8 - x1)
        output_final_move.append(output_move)

        letter_last_position_move = notations["{0}".format(y2)]
        output_last_position_move = "E" + " " + letter_last_position_move + "{0}".format(8 - x2)

        output_final_move.append(output_last_position_move)

        output_to_be_written_to_file_move = output_final_move[0] + " " + output_final_move[1].replace("E",
                                                                                                      "").replace(
            " ", "")
        print(output_to_be_written_to_file_move, end="", file=fp)
########################################################################################################################