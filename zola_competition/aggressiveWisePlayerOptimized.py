import math
import random
import time

class TimeoutException(Exception):
    pass

def shared_evaluate_state(game, state, root_player):
    """
    Euristica condivisa con Pesi Dinamici e Penalità di Paralisi.
    """
    winner = game.winner(state)
    if winner == root_player:
        return 100000
    if winner == game.opponent(root_player):
        return -100000
    if winner is not None:
        return 0

    opponent = game.opponent(root_player)

    root_count = state.count(root_player)
    opponent_count = state.count(opponent)
    total_pieces = root_count + opponent_count

    root_moves = game._actions_for_player(state, root_player)
    opponent_moves = game._actions_for_player(state, opponent)

    root_mobility = len(root_moves)
    opponent_mobility = len(opponent_moves)

    root_captures = sum(1 for m in root_moves if m[2] is True)
    opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

    # 1. Pesi Dinamici per la mobilità
    # All'inizio (64 pedine) il peso è basso, alla fine sale notevolmente.
    mobility_weight = 64.0 / max(1, total_pieces)

    score = 0
    score += (root_count - opponent_count) * 100
    score += (root_captures - opponent_captures) * 10
    score += (root_mobility - opponent_mobility) * mobility_weight

    # 2. Penalità di Paralisi (Gestione dei Bordi)
    edge_penalty = 0
    pieces_with_captures = set(m[0] for m in root_moves if m[2])
    
    for r in range(state.size):
        for c in range(state.size):
            if state.board[r][c] == root_player:
                # Se si trova sui bordi estremi
                if r == 0 or r == state.size - 1 or c == 0 or c == state.size - 1:
                    if (r, c) not in pieces_with_captures:
                        edge_penalty -= 5  # Penalità per inattività sul bordo

    score += edge_penalty
    return score


def aggressive_quiescence_search(game, state, alpha, beta, maximizing_player, root_player, start_time, time_limit, q_depth=0):
    if time.perf_counter() - start_time > time_limit:
        raise TimeoutException()

    stand_pat = shared_evaluate_state(game, state, root_player)

    if maximizing_player:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    if q_depth >= 5 or game.is_terminal(state):
        return stand_pat

    legal_moves = game.actions(state)
    captures = [m for m in legal_moves if m[2] is True]

    if not captures:
        return stand_pat

    if maximizing_player:
        value = -math.inf
        for move in captures:
            child_state = game.result(state, move)
            child_value = aggressive_quiescence_search(game, child_state, alpha, beta, False, root_player, start_time, time_limit, q_depth + 1)
            value = max(value, child_value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for move in captures:
            child_state = game.result(state, move)
            child_value = aggressive_quiescence_search(game, child_state, alpha, beta, True, root_player, start_time, time_limit, q_depth + 1)
            value = min(value, child_value)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def aggressive_alphabeta(game, state, depth, alpha, beta, maximizing_player, root_player, start_time, time_limit):
    if time.perf_counter() - start_time > time_limit:
        raise TimeoutException()

    legal_moves = game.actions(state)
    
    # Se raggiungiamo la profondità limite, attiviamo la Quiescence Search
    if depth == 0 or not legal_moves or game.is_terminal(state):
        return aggressive_quiescence_search(game, state, alpha, beta, maximizing_player, root_player, start_time, time_limit), None

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
                
        if captures and escapes and value <= -90000:
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

        if captures and escapes and value >= 90000:
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


class WiseZolaAIOptimized:
    def __init__(self, game, timeout=2.85):
        self.game = game
        self.timeout = timeout
        self.start_time = 0
        self.root_player = None

    def check_time(self):
        if time.perf_counter() - self.start_time > self.timeout:
            raise TimeoutException()

    def order_moves(self, moves):
        captures = []
        others = []
        for m in moves:
            if m[2]:  
                captures.append(m)
            else:
                others.append(m)
        return captures + others

    def quiescence_search(self, state, alpha, beta, maximizing_player, q_depth=0):
        self.check_time()
        
        stand_pat = shared_evaluate_state(self.game, state, self.root_player)

        if maximizing_player:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        if q_depth >= 5 or self.game.is_terminal(state):
            return stand_pat

        legal_moves = self.game.actions(state)
        captures = [m for m in legal_moves if m[2] is True]

        if not captures:
            return stand_pat

        if maximizing_player:
            value = -math.inf
            for move in captures:
                child_state = self.game.result(state, move)
                child_value = self.quiescence_search(child_state, alpha, beta, False, q_depth + 1)
                value = max(value, child_value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for move in captures:
                child_state = self.game.result(state, move)
                child_value = self.quiescence_search(child_state, alpha, beta, True, q_depth + 1)
                value = min(value, child_value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def alphabeta(self, state, depth, alpha, beta, maximizing_player):
        self.check_time()

        legal_moves = self.game.actions(state)
        
        if depth == 0 or self.game.is_terminal(state) or not legal_moves:
            # Passa alla Quiescence Search invece di restituire la valutazione statica
            return self.quiescence_search(state, alpha, beta, maximizing_player), None

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

        print(f"[AI {self.root_player}] (Wise-Opt mode) Profondità: {depth-1}. Mossa: {best_move}")
        return best_move

# ==========================================
# STRATEGIA COMBINATA MIGLIORATA
# ==========================================

def playerStrategy(game, state, timeout=3):
    root_player = state.to_move
    opponent = game.opponent(root_player)
    
    root_count = state.count(root_player)
    opponent_count = state.count(opponent)
    total_pieces = root_count + opponent_count

    if total_pieces <= 20 or root_count <= 10:
        safe_timeout = max(0.1, timeout - 0.15)
        ai_bot = WiseZolaAIOptimized(game, timeout=safe_timeout)
        return ai_bot.search(state)
    else:
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
                    
                if score >= 90000:
                    break
                    
                depth += 1
                
        except TimeoutException:
            pass
            
        print(f"[AI {state.to_move}] (Aggressive-Opt mode) Profondità: {depth-1}. Mossa: {best_move}")
        return best_move
