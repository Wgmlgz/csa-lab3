
(fn print_byte (n int) ((local_get n) (out 1)))

(fn print_str (s str)
  ((let i 0)
  (while (- i (. 's len)) (
    (let t (* (+ (. 's ptr) i)))
    (local_get_1 t)
    (out 1)
    (set i (+ i 1))
    ()))))

(fn print_n (n int)
  ((let cur 100000000)
  (let base 10)
  (let zero 48)
  (if (= n 0)
    (print_str "0")
    ((while (= 0 (% (/ n cur) base)) (
        (set cur (/ cur base)) ))
      (while cur (
        (print_byte (+ (% (/ n cur) base) zero))
        (set cur (/ cur base)) ))))
  ()))



(let heap (mem int 100))

(let len 20)
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


(fn sort (arr ints)
  ((let i 0)
  (while (< i (. 'arr len))
    ((let j (+ i 1))
    (while (< j (. 'arr len)) (
      (if (< (* (get arr j)) (* (get arr i)))
        ((let t (* (get arr j)))
        (pset (get arr j) (* (get arr i)))
        (pset (get arr i) t))
      ())
      (set j (+ j 1))
      ()))
    (set i (+ i 1))
    ()))))

(print_ints arr)
(fill arr)
(print_ints arr)
(sort arr)
(print_ints arr)
