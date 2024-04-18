(define (domain CircularNIm)
	(:objects ?v1 ?v2 ?v3 ?v4 ?v5)
	(:tercondition (and (= ?v1 0) (= ?v2 0) (= ?v3 0)  (= ?v4 0) (= ?v5 0)))
    (:constraint (and (>= ?v1 0) (>= ?v2 0) (>= ?v3 0)  (>= ?v4 0) (>= ?v5 0)))
    (:action take1
        :parameters (?k)
        :precondition (and (>= ?v1 ?k) (> ?k 0))
        :effect (and (assign ?v1 (- ?v1 ?k))))
    (:action take2
        :parameters (?k)
        :precondition (and (>= ?v2 ?k) (> ?k 0))
        :effect (and (assign ?v2 (- ?v2 ?k))))
    (:action take3
        :parameters (?k)
        :precondition (and (>= ?v3 ?k) (> ?k 0))
        :effect (and (assign ?v3 (- ?v3 ?k))))
    (:action take4
        :parameters (?k)
        :precondition (and (>= ?v4 ?k) (> ?k 0))
        :effect (and (assign ?v4 (- ?v4 ?k))))
    (:action take5
        :parameters (?k)
        :precondition (and (>= ?v5 ?k) (> ?k 0))
        :effect (and (assign ?v5 (- ?v5 ?k))))
)