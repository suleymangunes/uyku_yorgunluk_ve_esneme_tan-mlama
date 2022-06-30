from cvzone.FaceDetectionModule import FaceDetector
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import cv2
import math
import cvzone
import esneme_sinir

# webcamdan gorundu alindi
cap = cv2.VideoCapture(0)
# detector olarak goz agiz gibi degerleri bulan detector secildi
detector = FaceMeshDetector(maxFaces=1)
# ikinci detektor olarak yuzu bulan detektor secildi
detector2 = FaceDetector()
# agzin etrafini saran noktalarin id degerleri tanimlandi
idList = [0, 11, 12, 13, 14, 15, 16, 17, 37, 38, 39, 40, 41, 42, 61, 62, 72, 73, 74, 76, 77, 78, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 95, 146, 178, 179, 180, 181, 183, 184, 185, 191, 267, 268, 269, 270, 271, 272, 291, 292, 302, 304, 306, 307, 308, 310, 311, 312, 314, 315, 316, 317, 318, 319, 320, 321, 324, 325, 375, 402, 403, 404, 405, 407, 408, 409, 415]
# orani daha etkili bulmasi icin uzaklik ortalamasi degerlerini tutacak liste tanimlandi
uzaklikliste = []
# ploty ile canli sekilde degerlerin gosterilmesi icin grafik olusturuldu
grafg = 640  # grafigin genisligi
grafy = 360  # grafigin yuksekligi
graftop = 400  # grafigin kapsayacagi alanin ust noktasi
grafbot = 100  # grafigin kapsayacagi alanin alt noktasi
plotY = LivePlot(grafg, grafy, [grafbot, graftop], invert=True)
# sinir degeri belirlendi
altsinir = esneme_sinir.sinirbul("esneme")
ustsinir = esneme_sinir.sinirbul("normal")
sinir = altsinir + ((ustsinir - altsinir) * 0.28)


while True:
    # video uzerinden deneme yapilinca video bitince basa sarmasi icin kosul
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # goruntu okundu
    success, img = cap.read()

    # yuz uzerinden islem yapilacagi icin yuz bulunamazsa diye try except blogu kullanildi
    try:
        # yuz bulundu
        img, bboxs = detector2.findFaces(img)

        # yuzdeki degerlerin koordinatlari bulundu
        img, faces = detector.findFaceMesh(img, draw=False)
        # eger yuz bulundu ise
        if faces:
            # yuzun 0 id degeri bos tanimlandi
            face = faces[0]
            # agiz noktalarinin dongu uzerinden cizilmesi saglandi
            for id in idList:
                cv2.circle(img, (face[id][0], face[id][1]), 1,(0, 255, 255), cv2.FILLED)
            
            # agizda dikey ve yatay en uzun cizgi icin noktalar belirlendi
            lipt = (face[0][0], face[0][1])
            lipb = (face[17][0], face[17][1])
            lipr = (face[61][0], face[61][1])
            lipl = (face[291][0], face[291][1])
            cv2.line(img, lipt, lipb, (0, 200, 0), 2)  # dikey cizgi cizildi
            cv2.line(img, lipl, lipr, (0, 200, 0), 2)  # yatay cizgi cizildi

            # agizdaki en uzun diket ve en uzun yatay uzunluk bulunmasi icin noktalarin koordinatlari alindi
            x1 = face[0][0]
            y1 = face[0][1]
            x2 = face[17][0]
            y2 = face[17][1]

            z1 = face[61][0]
            k1 = face[61][1]
            z2 = face[291][0]
            k2 = face[291][1]

            # iki  nokta arasindaki uzaklik formulu ile uzaklik hesaplandi
            uzaklikd = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
            uzakliky = math.sqrt(math.pow(z1 - z2, 2) + math.pow(k1 - k2, 2))

            # yatay uzaklik dikey uzakliga bolunerek kameraya yaklasma ve uzaklasma durumlarinda bile sadece dikey uzunluk uzerine yanlislik onlendi
            # bu sayede her uzaklikta belirli oranda aciklik saglanirsa programin uyari vermesi saglandi
            uzaklikort = (uzakliky / uzaklikd) * 100
            # ortalama degeri listeye eklendi
            uzaklikliste.append(uzaklikort)

            # eger listedeki eleman sayisi 10 u gecerse ilk degerin silinmesi saglandi bu sayede son 10 deger uzerinden islem yapilmasi saglandi
            if len(uzaklikliste) > 10:
                uzaklikliste.pop(0)
            # listedeki elemanlarin ortalamasi alindi
            uzaklikortort = sum(uzaklikliste) / len(uzaklikliste)

            # eger deger sinirdan kucukse esneme durumu uyarisi saglandi
            if uzaklikortort < sinir:
                cvzone.putTextRect(img, 'esniyor', (50, 100), colorR=(0, 255, 0))

            # belirlenen sinirin tanimlanan grafik degerleri uzerinden koordinatinin bulunmasi saglandi
            sinirkoor = int(grafy - (grafy * (sinir - grafbot) / (graftop - grafbot)))
            # anlik olarak takip edilecek grafik olusturuldu
            imgPlot = plotY.update(uzaklikortort, (255, 0, 0))
            # sinir cizgisi cizildi
            cv2.line(imgPlot, (0, sinirkoor), (640, sinirkoor), (150, 150, 150), 2)
            # grafik ekranda gosterildi
            cv2.imshow("plot", imgPlot)
    # exception durumlarindan pas gecilmesi saglandi
    except Exception:
        pass
    
    # goruntunun ekranda gosterilmesi saglandi
    cv2.imshow("Image", img)
    
    # her kare arasinda 10 milisaniye birakildi ve q tusuna basilirsa cikilmasi saglandi
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# goruntu serbest birakildi
cap.release()
# pencelerin kapatilmasi saglandi
cv2.destroyAllWindows()
