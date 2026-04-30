import math
import random
import time

class TimeoutException(Exception):
    pass

def evaluate_state(game, state, root_player):
    """
    Valuta lo stato dando priorità al vantaggio materiale e alle mosse di cattura.
    """
    winner = game.winner(state)
    if winner == root_player:
        return 10000
    if winner == game.opponent(root_player):
        return -10000
    if winner is not None:
        return 0

    opponent = game.opponent(root_player)

    # Vantaggio di materiale (pezzi_nostri - pezzi_avversari)
    root_count = state.count(root_player)
    opponent_count = state.count(opponent)

    # Mobilità e potenziale di cattura (mosse_nostre - mosse_avversarie)
    root_moves = game._actions_for_player(state, root_player)
    opponent_moves = game._actions_for_player(state, opponent)

    root_mobility = len(root_moves)
    opponent_mobility = len(opponent_moves)

    # Mosse di cattura (mosse di cattura nostre - mosse di cattura avversarie)
    # Tuple: ((from_r, from_c), (to_r, to_c), is_capture)
    root_captures = sum(1 for m in root_moves if m[2] is True)
    opponent_captures = sum(1 for m in opponent_moves if m[2] is True)

    # Formula di punteggio (pesi regolabili)
    score = 0
    score += (root_count - opponent_count) * 100
    score += (root_captures - opponent_captures) * 10
    score += (root_mobility - opponent_mobility) * 1

    return score

def alphabeta(game, state, depth, alpha, beta, maximizing_player, root_player, start_time, time_limit):
    # Controllo tempo esaurito
    if time.perf_counter() - start_time > time_limit:
        raise TimeoutException()

    legal_moves = game.actions(state)
    if depth == 0 or not legal_moves or game.is_terminal(state):
        return evaluate_state(game, state, root_player), None

    # Separazione tra mosse di cattura e mosse di fuga (non cattura)
    captures = [m for m in legal_moves if m[2] is True]
    escapes = [m for m in legal_moves if m[2] is False]

    # Inizialmente esploriamo le catture se ci sono, altrimenti le fughe
    moves_to_search = captures if captures else escapes
    best_moves = []

    if maximizing_player:
        value = -math.inf
        for move in moves_to_search:
            child_state = game.result(state, move)
            child_value, _ = alphabeta(game, child_state, depth - 1, alpha, beta, False, root_player, start_time, time_limit)
            
            if child_value > value:
                value = child_value
                best_moves = [move]
            elif child_value == value:
                best_moves.append(move)
                
            alpha = max(alpha, value)
            if alpha >= beta:
                break
                
        # Se tutte le catture portano alla sconfitta, analizziamo le fughe
        if captures and escapes and value <= -9000:
            for move in escapes:
                child_state = game.result(state, move)
                child_value, _ = alphabeta(game, child_state, depth - 1, alpha, beta, False, root_player, start_time, time_limit)
                
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
            child_value, _ = alphabeta(game, child_state, depth - 1, alpha, beta, True, root_player, start_time, time_limit)
            
            if child_value < value:
                value = child_value
                best_moves = [move]
            elif child_value == value:
                best_moves.append(move)
                
            beta = min(beta, value)
            if alpha >= beta:
                break

        # Se il giocatore avversario (minimizzatore) vede che tutte le SUE catture
        # lo portano alla sconfitta (ovvero value >= 9000 dal nostro punto di vista),
        # allora lui analizzerà le SUE fughe.
        if captures and escapes and value >= 9000:
            for move in escapes:
                child_state = game.result(state, move)
                child_value, _ = alphabeta(game, child_state, depth - 1, alpha, beta, True, root_player, start_time, time_limit)
                
                if child_value < value:
                    value = child_value
                    best_moves = [move]
                elif child_value == value:
                    best_moves.append(move)
                    
                beta = min(beta, value)
                if alpha >= beta:
                    break
                    
        return value, random.choice(best_moves) if best_moves else None


def playerStrategy(game, state, timeout=3):
    """
    Strategia principale: Alpha-Beta Pruning con Iterative Deepening.
    """
    start_time = time.perf_counter()
    # Lasciamo 0.1s di margine per chiudere in sicurezza la funzione
    time_limit = timeout - 0.1 
    
    best_move = None
    legal_moves = game.actions(state)
    
    if not legal_moves:
        return None
    
    # Valore di default in caso l'eccezione scatti istantaneamente alla profondità 1
    best_move = random.choice(legal_moves)
    
    depth = 1
    try:
        while True:
            # Iterative deepening
            score, move = alphabeta(
                game, state, depth, 
                -math.inf, math.inf, 
                True, state.to_move, 
                start_time, time_limit
            )
            
            # Aggiorniamo la mossa migliore solo se la profondità è stata esplorata completamente
            if move is not None:
                best_move = move
                
            # Se abbiamo trovato una mossa che vince in modo certo, possiamo anche fermarci
            if score >= 9000:
                break
                
            depth += 1
            
    except TimeoutException:
        # Il tempo è scaduto, abbiamo catturato l'eccezione
        # Restituiamo la mossa migliore trovata alla profondità precedente completata
        pass
        
    print(f"[AI {state.to_move}] Profondità raggiunta: {depth-1}. Mossa scelta: {best_move}")
    return best_move
