(fn print (s str)
  ((let i 0)
  (while (- i (. 's len)) (
    (let t (* (+ (. 's ptr) i)))
    (local_get_1 t)
    (out 1)
    (set i (+ i 1))
    ()))))

(print "What is your name?\n")

(fn status int (
  (def (ready int))
  (io_status 0)
  (local_set ready)
  ready
))

(let heap (mem int 100))

(let len 20)
(def (arr ints))
(pset (-> 'arr ptr) heap)
(pset (-> 'arr len) len)

(fn print_byte (n int) ((local_get n) (out 1)))
(fn get (arr ints) (i int) int* (+ (. 'arr ptr) (* i 8)))
(fn print_ints (arr ints)
  ((let i 0)
  (while (< i (. 'arr len)) (
    (print_byte (* (get arr i)))
    (set i (+ i 1))
    ()))))

(let i 0)
(while (status) (
  (let t 0)
  (let r 0)
  (in 0)
  (local_set t)
  (pset (get arr i) t)
  (local_get t)
  (out 1)
  (set i (+ i 1))
))

(print "Hello, ")
(print_ints arr)
