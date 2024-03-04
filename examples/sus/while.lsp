(
  (let iter 10)
  (let a 65)

  (while (iter) (
    (local_get a)
    (out 1)
    (inc)
    (local_set a)

    (local_get iter)
    (dec)
    (local_set iter)
  ))
  (halt)
)