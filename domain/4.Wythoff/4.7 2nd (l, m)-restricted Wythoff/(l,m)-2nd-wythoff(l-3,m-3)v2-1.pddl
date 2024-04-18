(define (domain Wythoff_game)
    (:objects ?v1 ?v2)
    (:tercondition (and (= ?v1 0) (= ?v2 0)))
    (:constraint (and (>= ?v1 0) (>= ?v2 0) (<= ?v2 1)))
    (:action take1
        :parameters (?k ?l)
        :precondition (and (>= ?v1 ?k) (>= ?k 0)  (>= ?v2 ?l) (>= ?l 0)  (> (+ ?k ?l) 0) (or (and (< (- ?k ?l) 3) (> ?k ?l)) (and (< (- ?l ?k) 3) (> ?l ?k))  (> 3 ?k)  (> 3 ?l) ))
        :effect (and (assign ?v1 (- ?v1 ?k)) (assign ?v2 (- ?v2 ?l))))
)
    