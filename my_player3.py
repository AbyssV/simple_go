from read import readInput
from write import writeOutput
from host import GO


class MinimaxPlayer():
    def __init__(self):
        self.type = 'minimax'

    def get_input(self, go, piece_type):
        self.go = go
        # self.piece_type = piece_type

        # self.current_depth = 0
        self.max_depth = 4
        self.centre = (go.size // 2, go.size // 2)
        # all the entry in the board, by priority
        temp_dict = {}
        for i in range(self.go.size):
            for j in range(self.go.size):
                if (i == 0) or (j == 0) or (i == self.go.size - 1) or (j == self.go.size - 1):
                    temp_dict[(i,j)] = 0.6
                else:
                    if i == self.centre[0] and j == self.centre[1]:
                        temp_dict[(i, j)] = 1
                    else:
                        temp_dict[(i, j)] = 0.8
        self.candidate = []
        for key, value in sorted(temp_dict.items(), key = lambda d: d[1], reverse=True):
            self.candidate.append(key)

        # for the first two move, always take the centre
        if self.go.n_move <= 1 and self.go.valid_place_check(self.centre[0], self.centre[1], piece_type,
                                                             test_check=True):
            return self.centre
        else:
            # reorder possible placements so higher possibility to do pruning
            potential_movements = []
            lower_potential_movements = []
            for i, j in self.candidate:
                if self.go.valid_place_check(i, j, piece_type, test_check=True):
                    if self.if_neighbor(self.go, i, j, piece_type):
                        potential_movements.append((i, j))
                    else:
                        lower_potential_movements.append((i, j))
            potential_movements.extend(lower_potential_movements)

            # TODO: deal with 'PASS'
            # potential_movements.append((-1, -1))
            if not potential_movements: return 'PASS'

            v, action = self.MaxValue(self.go, piece_type, 0, potential_movements, float('-inf'), float('inf'))
            return action

    def MaxValue(self, go, piece_type, depth, potential_movements, alpha, beta):
        # if no action can be made in this level, what is the utility value?
        if depth + self.go.n_move >= self.go.max_move \
                or depth >= self.max_depth \
                or go.game_end(piece_type):
            # print(f'--------------MaxValue-----------------')
            # print(f'piece type: {piece_type}, current_depth: {depth}')
            score = self.compute_state(go, piece_type)
            # print('----------------------------------------')
            return score, 'PASS'

        v = float('-inf')
        res_action = None

        for action in potential_movements:
            next_level_go = go.copy_board()
            flag = next_level_go.place_chess(action[0], action[1], piece_type)
            if not flag:
                print('-----------------------ERROR-------------------------')
                next_level_go.visualize_board()
                raise ValueError(f'invalid move appear in MaxValue: {action}')
                print('-----------------------------------------------------')
            next_level_go.remove_died_pieces(3 - piece_type)

            next_level_potential_movements = []
            next_level_lower_potential_movements = []
            for i, j in self.candidate:
                if next_level_go.valid_place_check(i, j, 3 - piece_type, test_check=True):
                    if self.if_neighbor(next_level_go, i, j, 3 - piece_type):
                        next_level_potential_movements.append((i, j))
                    else:
                        next_level_lower_potential_movements.append((i, j))
            next_level_potential_movements.extend(next_level_lower_potential_movements)
            # potential_movements.append((-1, -1))

            next_level_v, next_level_action = self.MinValue(next_level_go, 3 - piece_type, depth + 1,
                                                            next_level_potential_movements, alpha, beta)
            if v < next_level_v:
                v = next_level_v
                res_action = action
            if v >= beta:
                return v, res_action
            alpha = max(alpha, v)
        return v, res_action

    def MinValue(self, go, piece_type, depth, potential_movements, alpha, beta):
        # if no action can be made in this level, what is the utility value?
        if depth + self.go.n_move >= self.go.max_move \
                or depth >= self.max_depth \
                or go.game_end(piece_type):
            # print(f'--------------MinValue-----------------')
            # print(f'piece type: {piece_type}, current_depth: {depth}')
            score = -1 * self.compute_state(go, piece_type)
            # print('----------------------------------------')
            return score, 'PASS'

        v = float('inf')
        res_action = None

        for action in potential_movements:
            next_level_go = go.copy_board()
            flag = next_level_go.place_chess(action[0], action[1], piece_type)
            if not flag:
                print('-----------------------ERROR-------------------------')
                next_level_go.visualize_board()
                raise ValueError(f'invalid move appear in MinValue: {action}')
                print('-----------------------------------------------------')
            next_level_go.remove_died_pieces(3 - piece_type)

            next_level_potential_movements = []
            next_level_lower_potential_movements = []
            for i, j in self.candidate:
                if next_level_go.valid_place_check(i, j, 3 - piece_type, test_check=True):
                    if self.if_neighbor(next_level_go, i, j, 3 - piece_type):
                        next_level_potential_movements.append((i, j))
                    else:
                        next_level_lower_potential_movements.append((i, j))
            next_level_potential_movements.extend(next_level_lower_potential_movements)
            # potential_movements.append((-1, -1))

            next_level_v, next_level_action = self.MaxValue(next_level_go, 3 - piece_type, depth + 1,
                                                            next_level_potential_movements, alpha, beta)
            if v > next_level_v:
                v = next_level_v
                res_action = action
            if v <= alpha:
                return v, res_action
            beta = min(beta, v)
        return v, res_action

    # ---------------------my function starts here----------------------------
    # return true if there is an opponent of current piece type
    def if_neighbor(self, go, i, j, piece_type):
        if go.board[i][j] == 0:
            neighbors = go.detect_neighbor(i, j)
            for r, c in neighbors:
                if go.board[r][c] == 3 - piece_type:
                    return True
        return False

    # find all the ally groups of piece type [[]...]
    def ally_in_the_board(self, go, piece_type):
        all_stones = set(
            (i, j) for i in range(len(go.board)) for j in range(len(go.board)) if go.board[i][j] == piece_type)
        result = []
        while all_stones:
            stone = all_stones.pop()
            ally_members = go.ally_dfs(stone[0], stone[1])
            # to compute connectivity, should be greater than 1
            if len(ally_members) > 1:
                result.append(ally_members)
                for pair in ally_members:
                    if pair != stone:  # pop already delete
                        all_stones.remove(pair)
        return result

    # count group liberty
    def count_liberty(self, go, piece_type):
        liberty = set()
        all_stones = set(
            (i, j) for i in range(len(go.board)) for j in range(len(go.board)) if go.board[i][j] == piece_type)

        for member in all_stones:
            neighbors = go.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if go.board[piece[0]][piece[1]] == 0:
                    liberty.add((piece[0], piece[1]))
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return len(liberty)

    # compute #piece type at edge
    def compute_edge(self, go, piece_type):
        count = 0
        for i in range(len(go.board)):
            for j in range(len(go.board)):
                if go.board[i][j] == piece_type and ((i == 0) or (j == 0) or \
                                                     (i == go.size - 1) or (j == go.size - 1)):
                    count += 1
        return count

    # TODO: more optimization
    # compute heuristic score of piece type, the action should be valid
    def compute_state(self, go, piece_type):
        player_score = go.score(piece_type)
        opponent_score = go.score(3 - piece_type)
        ally_group = len(self.ally_in_the_board(go, piece_type))
        opponent_group = len(self.ally_in_the_board(go, 3-piece_type))
        ally_liberty = self.count_liberty(go, piece_type)
        opponent_liberty = self.count_liberty(go, 3 - piece_type)
        player_edge_punishment = self.compute_edge(go, piece_type)
        # opponent_edge_punishment = self.compute_edge(go, 3 - piece_type)
        heuristic_score = (player_score - opponent_score) * 30 \
                          + (ally_liberty - opponent_liberty) \
                          + (ally_group - opponent_group) \
                          - (player_edge_punishment)
        if piece_type == 2:
            heuristic_score += go.komi

        # check heuristic function
        # go.visualize_board()
        # print(ally_group)
        # print(f'piece type: {piece_type}, \
        # ({player_score} - {opponent_score}) * 30 + \
        # ({ally_liberty} - {opponent_liberty})  + \
        # ({ally_group} - {opponent_group}) * 2  - \
        # ({player_edge_punishment}) * 0.2 = {heuristic_score}')

        return heuristic_score
    # ------------------my function ends here----------------------------


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    # go.visualize_board()
    player = MinimaxPlayer()

    # check utility function
    # print(player.ally_in_the_board(go, 2))
    # print(player.count_liberty(go, 2))
    # print(player.compute_edge(go, 2))
    # print(player.compute_state(go, 2))

    action = player.get_input(go, piece_type)
    # print(action)
    writeOutput(action)
