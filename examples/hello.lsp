(fn print (s str)
  ((let i 0)
  (while (- i (. 's len)) (
    (let t (* (+ (. 's ptr) i)))
    (local_get_1 t)
    (out 1)
    (set i (+ i 1))
    ()))))

(print "Hello world!")