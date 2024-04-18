(define (domain CircularNIm)
	(:objects ?v1 ?v2 ?v3 ?v4 ?v5)
	(:tercondition (and (= ?v1 0) (= ?v2 0) (= ?v3 0)  (= ?v4 0) (= ?v5 0)))
    (:constraint (and (>= ?v1 0) (>= ?v2 0) (>= ?v3 0)  (>= ?v4 0) (>= ?v5 0)))
    (:action take1
        :parameters (?k1 ?k2 ?k3 ?k4)
        :precondition (and (>= ?v1 ?k1) (>= ?v2 ?k2) (>= ?v3 ?k3) (>= ?v4 ?k4) (>= ?k1 0) (>= ?k2 0) (>= ?k3 0) (>= ?k4 0) (>= (+ ?k1 (+ ?k2 (+ ?k3 ?k4))) 1))
        :effect (and (assign ?v1 (- ?v1 ?k1)) (assign ?v2 (- ?v2 ?k2)) (assign ?v3 (- ?v3 ?k3))  (assign ?v4 (- ?v4 ?k4))))
    (:action take2
        :parameters (?k1 ?k2 ?k3 ?k4)
        :precondition (and  (>= ?v2 ?k1) (>= ?v3 ?k3) (>= ?v4 ?k4) (>= ?v5 ?k5) (>= ?k1 0) (>= ?k2 0) (>= ?k3 0) (>= ?k4 0) (>= (+ ?k1 (+ ?k2 (+ ?k3 ?k4))) 1))
        :effect (and (assign ?v2 (- ?v2 ?k1)) (assign ?v3 (- ?v3 ?k2)) (assign ?v4 (- ?v4 ?k3))  (assign ?v5 (- ?v5 ?k4))))
    (:action take3
        :parameters (?k1 ?k2 ?k3 ?k4)
        :precondition (and (>= ?v3 ?k1) (>= ?v4 ?k2) (>= ?v5 ?k3) (>= ?v1 ?k4) (>= ?k1 0) (>= ?k2 0) (>= ?k3 0) (>= ?k4 0) (>= (+ ?k1 (+ ?k2 (+ ?k3 ?k4))) 1))
        :effect (and (assign ?v3 (- ?v3 ?k1)) (assign ?v4 (- ?v4 ?k2)) (assign ?v5 (- ?v5 ?k3))  (assign ?v1 (- ?v1 ?k4)))) 
    (:action take4
        :parameters (?k1 ?k2 ?k3 ?k4)
        :precondition (and (>= ?v4 ?k1) (>= ?v5 ?k2) (>= ?v1 ?k3) (>= ?v2 ?k4) (>= ?k1 0) (>= ?k2 0) (>= ?k3 0) (>= ?k4 0) (>= (+ ?k1 (+ ?k2 (+ ?k3 ?k4))) 1))
        :effect (and (assign ?v4 (- ?v4 ?k1)) (assign ?v5 (- ?v5 ?k2)) (assign ?v1 (- ?v1 ?k3))  (assign ?v2 (- ?v2 ?k4))))
    (:action take5
        :parameters (?k1 ?k2 ?k3 ?k4)
        :precondition (and (>= ?v5 ?k1) (>= ?v1 ?k2) (>= ?v2 ?k3) (>= ?v3 ?k4) (>= ?k1 0) (>= ?k2 0) (>= ?k3 0) (>= ?k4 0) (>= (+ ?k1 (+ ?k2 (+ ?k3 ?k4))) 1))
        :effect (and (assign ?v5 (- ?v5 ?k1)) (assign ?v1 (- ?v1 ?k2)) (assign ?v2 (- ?v2 ?k3))  (assign ?v3 (- ?v3 ?k4))))

)