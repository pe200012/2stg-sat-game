
(define (domain Wythoff_game)
	(:objects ?v1 ?v2)
	(:tercondition (and (= ?v1 0) (= ?v2 0)))
	(:constraint (and (>= ?v1 0) (>= ?v2 0)(<= ?v2 4)))
	(:action take1
		:parameters (?k)
		:precondition (and (>= ?v1 ?k) (> ?k 0) (%= ?k 2 1))
		:effect (assign ?v1 (- ?v1 ?k)))
	(:action take2
		:parameters (?k)
		:precondition (and (>= ?v2 ?k) (> ?k 0) (%= ?k 2 1))
		:effect (assign ?v2 (- ?v2 ?k)))
	(:action take3
		:parameters (?k ?l)
		:precondition (and (>= ?v1 ?k) (> ?k 0)   (>= ?v2 ?l) (> ?l 0)  (or(and(>= ?k ?l) (< ?k  (+ 4 (+ ?l (+ ?l (+ ?l (+ ?l ?l))))))) (and(>= ?l ?k) (< ?l (+ 4 (+ ?k (+ ?k (+ ?k (+ ?k ?k)))))))))
		:effect (and (assign ?v1 (- ?v1 ?k)) (assign ?v2 (- ?v2 ?l))))
)
    