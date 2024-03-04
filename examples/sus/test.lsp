(
  (fn print_u64 (n u64) (
    (let cur 100000000)
    (let base 10)
    (let zero 48)

    (while cur (
      (let t (+ (% (/ n cur) base) zero) )
      (local_get t)
      (out 1)
      (set cur (/ cur base)) ))
    ()
  ))
  
  (fn factorial (n u64) u64 (if (= n 0) 1 (* n (factorial (- n 1)))))
  (fn fib (n u64) u64 (if (eq n 0) 0 (if (eq n 1) 1 (add (fib (sub n 1)) (fib (sub n 2))))))
  ;; ;; (fn ttt (n u64) u64 (if (eq n 0) 2 3))
  ;; ;; (let a (if 0 2 3))
  ;; ;; (let b (factorial 5))
  ;; (let b (fib 18))
  ;; 0 1 1 2 3 5 8 13 21
  ;; 0 1 2 3 4 5 6 7  8  9
  ;; (print_u64 a)
  (print_u64 (factorial (7)))
  (print_u64 666)
  (halt)
)