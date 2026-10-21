# Sistem Informatic pentru Gestiunea Activităților de Service și Garanții Electrocasnice

## 📌 Informații Student
* **Student:** [Numele Tău]
* **Disciplina:** Proiectarea Bazelor de Date
* **An de Studiu:** III
* **Cadru Didactic:** [Nume Profesor]

---

## 📂 Cuprins
1. [1. Scopul și Obiectivele Proiectului](#1-scopul-și-obiectivele-proiectului)
   * [1.1 Scopul Proiectului](#11-scopul-proiectului)
   * [1.2 Obiectivele Proiectului](#12-obiectivele-proiectului)

---

## 1. Scopul și Obiectivele Proiectului

### 1.1 Scopul Proiectului
Scopul principal al acestui proiect este proiectarea și implementarea unei baze de date relaționale centralizate, dedicate unui service autorizat de electrocasnice. Utilitatea sa practică constă în automatizarea validării garanțiilor, optimizarea distribuției sarcinilor către tehnicieni în funcție de disponibilitate și specializare, precum și urmărirea în timp real a pieselor de schimb de către aceștia, permițându-le să intervină asupra aparatelor din momentul în care piesele ajung în service.

Baza de date va fi însoțită de o aplicație web accesibilă de la distanță, nu doar din rețeaua locală, permițând spre exemplu unui tehnician să plănuiască și să organizeze din timp ordinea diagnosticării produselor. Acest aspect este deosebit de util dacă tehnicienilor li se atribuie solicitări în zile în care aceștia sunt absenți din diferite motive din service.

### 1.2 Obiectivele Proiectului
Sistemul informatic va deservi trei categorii majore de utilizatori din cadrul companiei, având drepturi de acces și funcționalități clar delimitate în fluxul operațional:

*   **👨‍💼 Administrator:** Deține controlul total asupra configurării sistemului. Acesta are dreptul de a adăuga utilizatori noi, de a modifica utilizatorii existenți și de a șterge utilizatori din cadrul aplicației.
*   **💻 Operator:** Reprezintă interfața logistică și de comunicare a service-ului. Operatorul preia solicitările clienților (fizic la recepție), înregistrează datele de identificare ale clienților și ale aparatelor electrocasnice aduse în service și validează automat statutul de garanție în funcție de documentele de achiziție. Totodată, introduce descrierea inițială a defectului reclamat și atribuie solicitările către tehnicieni în funcție de disponibilitatea și specializarea acestora.
*   **🔧 Tehnician:** Interacționează direct cu fluxul tehnic de reparație prin intermediul aplicației web, având posibilitatea de a accesa sistemul de la distanță. Tehnicianul își consultă lista de tichete alocate, își organizează și planifică din timp ordinea diagnosticării produselor (funcționalitate critică pentru eficientizarea muncii în perioadele în care este absent fizic din service) și notează diagnosticul final. Pe parcursul intervenției, actualizează stadiul tichetului (*În reparație*, *Așteaptă piese*, *Finalizat* etc.) și înregistrează piesele de schimb necesare. Dat fiind că păstrarea unui stoc centralizat este ineficientă și reprezintă o decizie financiară precară din cauza lipsei de compatibilitate între branduri, modele și versiuni, piesele necesare vor fi comandate în regim *on demand*, pe baza ID-ului de tichet, direct prin intermediul aplicației.
