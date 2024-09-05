# Proves amb càmeres:

## Raspberry 4:

  <img width="970" alt="image" src="https://github.com/user-attachments/assets/99bbdc0f-a610-4bf9-983d-d54297f82999">

  Conclusions:
  - Es triga 257 ms a llegir la imatge
  - Es triga 40 ms a processar la imatge
  - Des de que iniciem la lectura fins que sabem la posicional passen 323 ms

## TPTEK:

  - Anem a llegir: 17:54:39:467
  - Imatge llegida: 17:54:39:483
  - Imatge passada a grisos: 17:54:39:493
  
  <img width="867" alt="image" src="https://github.com/user-attachments/assets/ee0c514f-3978-4e99-8690-0b094c9ff02a">
  
  Conclusions:
  - La imatge arriba amb 2,5 segons de retard
  - La imatge es llegeix de la càmera en 16 ms
  - La imatge es passa a grisos en 10 ms

## DAHUA:

  - Anem a llegir: 18:07:34:851
  - Imatge llegida: 18:07:34:854
  - Imatge passada a grisos: 18:07:34:860

  <img width="386" alt="image" src="https://github.com/user-attachments/assets/789b181d-ea4e-4a8c-a530-e0ad80110261">

  Conclusions:
  - La imatge arriba amb 2 segons de retard
  - La imatge es llegeix de la càmera en 3 ms
  - La imatge es passa a grisos en 6 ms

Problema resolt! El retard en la lectura no sé exactament per què és però deu ser per la generació d'algun buffer o alguna cosa similar. Passa amb la primera lectura d'imatge. Si es llegeixen vàries imatges llavors el retard és d'uns 100ms.

<img width="496" alt="image" src="https://github.com/user-attachments/assets/9db8aa7e-5c48-44bd-8f1c-5932521015f4">

