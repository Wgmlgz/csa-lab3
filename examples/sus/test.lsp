(
  (setq iter 10)
  (setq a 65)

  (while (iter) (
    (stack_get a)
    (out 1)
    (inc)
    (stack_set a)

    (stack_get iter)
    (dec)
    (stack_set iter)
  ))
  (halt)
)