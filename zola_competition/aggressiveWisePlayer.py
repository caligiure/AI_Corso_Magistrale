import math
import random
import time

class TimeoutException(Exception):
    pass

# ==========================================
# COMPONENTI DI AGGRESSIVE PLAYER
# ==========================================

def aggressive_evaluate_state(game, state, root_player):
    winner = game.winner(state)
    if winner == root_player:
        return 10000
    if winner == game.opponent(root_player):
        return -10000
    if winner is not None:
        return 0

    opponent = game.opponent(root_player)

    root_count = state.count(root_player)
    opponent_count = state.count(opponent)

    root_moves = game._actions_for_player(state, root_player)
    opponent_moves = game._actions_for_player(state, opponent)

    root_mobility = len(root_moves)
    opponent_mobility = len(opponent_moves)

    root_captures = sum(1 for m in root_moves if m[2] is True)
    opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

    score = 0
    score += (root_count - opponent_count) * 100
    score += (root_captures - opponent_captures) * 10
    score += (root_mobility - opponent_mobility) * 1

    return score

def aggressive_alphabeta(game, state, depth, alpha, beta, maximizing_player, root_player, start_time, time_limit):
    if time.perf_counter() - start_time > time_limit:
        raise TimeoutException()

    legal_moves = game.actions(state)
    if depth == 0 or not legal_moves or game.is_terminal(state):
        return aggressive_evaluate_state(game, state, root_player), None

    captures = [m for m in legal_moves if m[2] is True]
    escapes = [m for m in legal_moves if m[2] is False]

    moves_to_search = captures if captures else escapes
    best_moves = []

    if maximizing_player:
        value = -math.inf
        for move in moves_to_search:
            child_state = game.result(state, move)
            child_value, _ = aggressive_alphabeta(game, child_state, depth - 1, alpha, beta, False, root_player, start_time, time_limit)
            
            if child_value > value:
                value = child_value
                best_moves = [move]
            elif child_value == value:
                best_moves.append(move)
                
            alpha = max(alpha, value)
            if alpha >= beta:
                break
                
        if captures and escapes and value <= -9000:
            for move in escapes:
                child_state = game.result(state, move)
                child_value, _ = aggressive_alphabeta(game, child_state, depth - 1, alpha, beta, False, root_player, start_time, time_limit)
                
                if child_value > value:
                    value = child_value
                    best_moves = [move]
                elif child_value == value:
                    best_moves.append(move)
                    
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
                    
        return value, random.choice(best_moves) if best_moves else None

    else:
        value = math.inf
        for move in moves_to_search:
            child_state = game.result(state, move)
            child_value, _ = aggressive_alphabeta(game, child_state, depth - 1, alpha, beta, True, root_player, start_time, time_limit)
            
            if child_value < value:
                value = child_value
                best_moves = [move]
            elif child_value == value:
                best_moves.append(move)
                
            beta = min(beta, value)
            if alpha >= beta:
                break

        if captures and escapes and value >= 9000:
            for move in escapes:
                child_state = game.result(state, move)
                child_value, _ = aggressive_alphabeta(game, child_state, depth - 1, alpha, beta, True, root_player, start_time, time_limit)
                
                if child_value < value:
                    value = child_value
                    best_moves = [move]
                elif child_value == value:
                    best_moves.append(move)
                    
                beta = min(beta, value)
                if alpha >= beta:
                    break
                    
        return value, random.choice(best_moves) if best_moves else None


# ==========================================
# COMPONENTI DI WISE PLAYER OPTIMIZED
# ==========================================

class WiseZolaAI:
    def __init__(self, game, timeout=2.85):
        self.game = game
        self.timeout = timeout
        self.start_time = 0
        self.root_player = None

    def check_time(self):
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def evaluate_state(self, state):
        winner = self.game.winner(state)
        if winner == self.root_player:
            return 100_000
        if winner == self.game.opponent(self.root_player):
            return -100_000
        if winner is not None:
            return 0 

        opponent = self.game.opponent(self.root_player)

        root_count = state.count(self.root_player)
        opponent_count = state.count(opponent)

        root_moves = self.game._actions_for_player(state, self.root_player)
        opponent_moves = self.game._actions_for_player(state, opponent)

        root_mobility = len(root_moves)
        opponent_mobility = len(opponent_moves)

        root_captures = sum(1 for m in root_moves if m[2] is True)
        opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

        score = 0
        score += (root_count - opponent_count) * 100
        score += (root_captures - opponent_captures) * 10
        score += (root_mobility - opponent_mobility) * 1

        return score

    def order_moves(self, moves):
        captures = []
        others = []
        for m in moves:
            if m[2]:  
                captures.append(m)
            else:
                others.append(m)
                
        return captures + others

    def alphabeta(self, state, depth, alpha, beta, maximizing_player):
        self.check_time()

        legal_moves = self.game.actions(state)
        
        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            return self.evaluate_state(state), None

        legal_moves = self.order_moves(legal_moves)
        best_move = None

        if maximizing_player:
            value = -math.inf
            for move in legal_moves:
                child_state = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, False
                )

                if child_value > value:
                    value = child_value
                    best_move = move

                alpha = max(alpha, value)
                if alpha >= beta:
                    break  

            return value, best_move
        else:
            value = math.inf
            for move in legal_moves:
                child_state = self.game.result(state, move)
                child_value, _ = self.alphabeta(
                    child_state, depth - 1, alpha, beta, True
                )

                if child_value < value:
                    value = child_value
                    best_move = move

                beta = min(beta, value)
                if alpha >= beta:
                    break  

            return value, best_move

    def search(self, state):
        self.root_player = state.to_move
        self.start_time = time.perf_counter()

        legal_moves = self.game.actions(state)
        if not legal_moves:
            return None

        best_move = random.choice(legal_moves) 
        
        depth = 1
        try:
            while True:
                val, current_best_move = self.alphabeta(
                    state, depth, -math.inf, math.inf, True
                )
                
                if current_best_move is not None:
                    best_move = current_best_move

                if val >= 90_000:
                    break
                    
                depth += 1
                
        except TimeoutException:
            pass

        print(f"[AI {self.root_player}] (Wise mode) Profondità raggiunta: {depth-1}. Mossa scelta: {best_move}")
        
        return best_move

# ==========================================
# STRATEGIA COMBINATA (Aggressive -> Wise)
# ==========================================

def playerStrategy(game, state, timeout=3):
    root_player = state.to_move
    opponent = game.opponent(root_player)
    
    root_count = state.count(root_player)
    opponent_count = state.count(opponent)
    total_pieces = root_count + opponent_count

    # Condizione: numero di pezzi totali <= 20 oppure i propri pezzi <= 10
    if total_pieces <= 20 or root_count <= 10:
        # Usa il comportamento di wisePlayerOptimized
        safe_timeout = max(0.1, timeout - 0.15)
        ai_bot = WiseZolaAI(game, timeout=safe_timeout)
        return ai_bot.search(state)
    else:
        # Usa il comportamento di aggressivePlayer
        start_time = time.perf_counter()
        time_limit = timeout - 0.1 
        
        best_move = None
        legal_moves = game.actions(state)
        
        if not legal_moves:
            return None
        
        best_move = random.choice(legal_moves)
        
        depth = 1
        try:
            while True:
                score, move = aggressive_alphabeta(
                    game, state, depth, 
                    -math.inf, math.inf, 
                    True, state.to_move, 
                    start_time, time_limit
                )
                
                if move is not None:
                    best_move = move
                    
                if score >= 9000:
                    break
                    
                depth += 1
                
        except TimeoutException:
            pass
            
        print(f"[AI {state.to_move}] (Aggressive mode) Profondità raggiunta: {depth-1}. Mossa scelta: {best_move}")
        return best_move
