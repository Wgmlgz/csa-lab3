(import "./std")

(let upper_bound 4000000)
(let a 1)
(let b 2)
(let sum 0)

(while (< b upper_bound) (
  (if (% b 2) (0) (set sum (+ sum b)))
  (let t b)
  (set b (+ a b))
  (set a t)))

(print_n sum)
