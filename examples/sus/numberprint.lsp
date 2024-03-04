(
  (let n 2281337)
  ((((
    (let g 2)
    ((g))
  ))))
  (let base (((((10))))))
  (let zero 48)

  (while (n) (
    (local_get n)
    (rem_local base)
    (add_local zero)
    (out 1)
    (local_get n)
    (div_local base)
    (local_set n)
  ))
  (halt)
)