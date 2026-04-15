(define (domain knights-tour)
    ; Questo requirement serve per poter gestire la
    ; negazione nelle precondizioni, in particolare
    ; bisogna valutare solamente le mosse che ci portano
    ; alle celle non visitate
    (:requirements :negative-preconditions)

    (:predicates
        (at ?square)
        (visited ?square)
        (valid_move ?square_from ?square_to)
    )

    (:action move
        :parameters (?from ?to)
        :precondition (and (at ?from)
            (valid_move ?from ?to)
            (not (visited ?to)))
        :effect (and (not (at ?from))
            (at ?to)
            (visited ?to))
    )
)