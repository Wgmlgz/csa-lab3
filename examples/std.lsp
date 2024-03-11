
(fn print_byte (n int) ((local_get n) (out 1)))

(fn print_str (s str)
  ((let i 0)
  (while (- i (. 's len)) (
    (let t (* (+ (. 's ptr) i)))
    (local_get_1 t)
    (out 1)
    (set i (+ i 1))
    ()))))

(fn nl (print_str "\n"))

(fn print (s str)
  ((print_str(s))
  (nl)))


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

(fn factorial (n int) int  
  (if (= n 0) 1 (* n (factorial (- n 1)))))

(fn fib (n int) int  
  (if (= n 0)
    0
    (if (= n 1)
      1
      (+ (fib (- n 1)) (fib (- n 2))))))
