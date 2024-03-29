(import "./std")

(let heap (mem int 900))

(let len 900)
(def (arr ints))
(pset (-> 'arr ptr) heap)
(pset (-> 'arr len) len)


(fn get (arr ints) (i int) int* (+ (. 'arr ptr) (* i 8)))

(fn print_ints (arr ints)
  ((print_str "[")
  (let i 0)
  (while (< i (. 'arr len)) (
    (if i (print_str ", ") ())
    (print_n (* (get arr i)))
    (set i (+ i 1))
    ()
  ))
  (print_str "]\n")))

(fn fill (arr ints)
  ((let i 0)
  (while (< i (. 'arr len)) (
    (pset (get arr i) (% (* (+ i 666) 666342123) 100))
    (set i (+ i 1))
    ()))))


(fn sum (arr ints) int
  ((let i 0)
  (let s 0)
  (while (< i 30)
    ((let j 0)
    (while (< j 30) (
      (set s (+ s (* (+ (. 'arr ptr) (* 8 (+ (* i 30) j))))))
      (set j (+ j 1))
      ()))
    (set i (+ i 1))
    ()))
  s))

(fill arr)
(print_ints arr)
(print_n (sum arr))
