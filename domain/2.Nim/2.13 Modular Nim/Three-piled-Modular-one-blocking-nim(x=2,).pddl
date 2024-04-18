(define (domain Three-piled-Modular-blocking-nim)
	(:objects ?v1 ?v2 ?v3)
	(:tercondition (and (= ?v1 0) (= ?v2 0) (= ?v3 0)))
    (:constraint (and (>= ?v1 0) (>= ?v2 0) (>= ?v3 0) ))
    (:action take1
        :parameters (?k)
        :precondition (and (>= ?v1 ?k) (> ?k 0) (or (%= ?k 3 0) (%= ?k 3 1)))
        :effect (assign ?v1 (- ?v1 ?k)))
    (:action take2
        :parameters (?k)
        :precondition (and (>= ?v2 ?k) (> ?k 0) (or (%= ?k 3 0) (%= ?k 3 1)))
        :effect (assign ?v2 (- ?v2 ?k)))
    (:action take2
        :parameters (?k)
        :precondition (and (>= ?v3 ?k) (> ?k 0) (or (%= ?k 3 0) (%= ?k 3 1)))
        :effect (assign ?v3 (- ?v2 ?k)))
)