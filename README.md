# newsfaces

Work in Progress

## Example Session

Parameters TBD, but to give a rough idea of usage:

```
$ newsfaces scrape cnn
fetched 10000 articles in 3:00:00
  2000 returned errors
  8000 were fetched successfully

$ newsfaces extract
processed 8000 articles in 0:20:00
  1000 had no images
  12000 images extracted from 7000 articles

$ newsfaces identify
processed 12000 images in 0:40:00
  1000 -> h_clinton
  1000 -> m_rubio
  2000 -> no_face
  2000 -> unknown_face
  3000 -> d_trump
  3000 -> j_biden

$ newsfaces browse
opening http://localhost:9999
(opens an interface where we can visually examine results)
```

