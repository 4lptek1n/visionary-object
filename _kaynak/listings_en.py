# -*- coding: utf-8 -*-
"""Listing titles and descriptions in the 1stDibs house format.

1stDibs title formula observed on live listings:
  [Period] [Medium] [School/Origin] [Subject], [Framed/Signed], [Date]
  e.g. "Wading, Impressionist Oil on Board Painting, Late 19th Century, Signed"
       "17th Century Oil on Canvas Italian Antique Painting Landscape with Goats, 1680"

1stDibs description formula observed:
  ARTIST NAME (nationality, dates) Title, medium, signature location, dimensions,
  then condition/provenance notes.

Applied here to our own items. Facts only: what is legible in the photographs,
plus subject matter visible in the image. Nothing invented.
"""

L = {
1:  ("Reclining Nude Charcoal Drawing, Signed and Numbered, Gold Frame, 1973",
     "G. GOUNARO. Reclining nude, charcoal on paper, signed and dated lower right 'G. Gounaro 73', "
     "numbered 20/200. Presented in a gold moulded frame under glass. Horizontal format."),
2:  ("Seated Nude Charcoal Drawing, Signed and Numbered, Black Frame, 1973",
     "G. GOUNARO. Seated nude, charcoal on paper, signed and dated 'G. Gounaro 73', numbered 35/200. "
     "Presented in a black moulded frame with white mat under glass. Vertical format."),
3:  ("Antique Dutch School Oil on Panel Interior Scene with Serving Boy, Gilt Frame",
     "Antique interior scene, oil on panel, depicting a young servant raising a jug in a vaulted kitchen. "
     "Housed in a carved and gilded frame with a brass name plaque on the lower rail."),
4:  ("Antique Flemish School Oil Painting, Merry Company, Carved Oval Giltwood Frame",
     "Antique group scene, oil on panel, showing a company of figures in period dress gathered around a "
     "draped table. Presented in a pierced and carved oval giltwood frame."),
5:  ("Framed Landscape Print with Children in a Meadow, Double Mat, Wood Frame",
     "Landscape with two children seated in tall summer grass beneath a stand of trees. Framed in a dark "
     "wood moulding with a double mat under glass."),
6:  ("Antique Hand-Worked Lace Panel, Floral Medallion, Framed Under Glass",
     "Hand-worked needle lace panel with a central floral medallion within a scalloped border. Mounted on "
     "a dark ground and framed under glass. Vertical format."),
7:  ("Framed Winter Woodland Stream Print with Certificate of Authenticity",
     "Winter landscape with a stream running through bare woodland. Titled plaque on the mat. Accompanied "
     "by a certificate of authenticity, photographed with the lot. Framed in dark wood under glass."),
8:  ("Mid-Century Style Abstract Oil on Canvas, Vertical Colour Bands, Unframed",
     "Abstract composition in vertical bands of red, yellow, blue and green over a dark ground. Oil on "
     "canvas, unframed, with visible impasto and canvas texture."),
9:  ("Original Serigraph Garden Landscape, Pencil Signed, Certificate of Authenticity",
     "Garden landscape, original serigraph, pencil signed and titled in the lower margin. Published by "
     "Fine Arts Gallery, Inc., Ardmore, PA; certificate of authenticity affixed to the reverse. "
     "Framed with a burgundy and cream mat under glass."),
10: ("Modern Oil on Canvas, Woman in a Red Dress at a Harbour Cafe, Giltwood Frame",
     "Figurative composition of a seated woman in a red dress at a harbour cafe, with sailing vessels "
     "beyond. Oil on canvas, signed lower right in yellow. Presented in a carved giltwood frame."),
11: ("Impressionist Oil Painting, Market Stalls with Parasols, Gilt Frame",
     "Street market with produce stalls under striped parasols. Oil on canvas, signed lower right. "
     "Presented in a moulded gilt frame."),
12: ("Framed Watercolour of a Canal Street, Silvered Frame, Wide Mat",
     "Architectural view of a canal street with figures. Watercolour on paper, presented with a wide mat "
     "in a silvered moulded frame under glass."),
13: ("Antique Engraving, Figures Beneath a Tree, Carved Silvered Frame",
     "Engraving on paper depicting two figures resting beneath a large tree. Presented with a rose mat in "
     "a carved silvered frame under glass."),
14: ("Divan Japonais Lithographic Poster After Toulouse-Lautrec, Black Frame",
     "Lithographic poster after the Divan Japonais design, printed in black, ochre and cream. Presented "
     "in a black moulded frame under glass."),
15: ("Japanese Woodblock Style Portrait of a Woman, Pencil Signed, Carved Gilt Frame",
     "Portrait of a woman in a patterned kimono, pencil signed in the lower margin. Presented with a pink "
     "mat in a carved gilt frame under glass."),
16: ("Chinese School Landscape Painting with Calligraphic Inscription, Framed",
     "Landscape with willows and distant hills, calligraphic inscription and seal upper left. Framed in a "
     "burgundy moulding under glass."),
17: ("Jean Sariano Relief Embossed Etching 'Going West', Artist's Proof, 1975",
     "JEAN SARIANO (Algerian, b. 1942) 'Going West', 1975. Original relief embossed etching, inscribed "
     "'Artist's Proof' lower left, titled centre and signed lower right. Edition of 50 plus 20 proofs. "
     "Certificate of authenticity and artist biography label affixed to the reverse; gallery inventory "
     "number 96-21-8. Long horizontal format."),
18: ("'Dancing Tulips' Embossed Watercolour, Signed and Dated 2005, Grey Frame",
     "'Dancing Tulips', embossed watercolour of tulips against a stone wall, inscribed with the title, "
     "artist and date 7-2005 within the image. Framed in a grey wood moulding with mat under glass."),
19: ("Japanese Ukiyo-e Style Woodblock Print, Street Procession, Framed",
     "Street procession with a yellow palanquin and attendant figures. Woodblock print on paper, presented "
     "with a mat in a dark moulded frame under glass."),
20: ("Japanese Woodblock Style Figure Print, Actor in Yellow, Wood Frame",
     "Standing figure in yellow costume against a plain ground. Print on paper, presented with a mat in a "
     "wood frame under glass."),
21: ("Framed Papyrus Painting, Warriors with Spears, Yellow Mat, Dark Frame",
     "Painting on papyrus depicting a file of warriors carrying spears, in red, ochre and black. Presented "
     "with a yellow mat in a dark wood frame under glass."),
22: ("Show Boat Broadway Poster, Harold Prince Production, Silver Frame",
     "Show Boat theatrical poster, book and lyrics by Oscar Hammerstein II, based on the novel by Edna "
     "Ferber, choreography by Susan Stroman, directed by Harold Prince. Offset lithograph, presented in a "
     "silvered aluminium frame under glass."),
23: ("'Sunset Shadows' Signed and Numbered Serigraph, Wide Mat, Wood Frame",
     "EHRLICH / SACCO 'Sunset Shadows'. Serigraph of trees against a sunset sky, pencil signed, titled and "
     "numbered from an edition of 200 in the lower margin. Presented with a wide white mat in a heavy wood "
     "frame under glass."),
24: ("Antique Style Charcoal Portrait of a Bearded Man in a Wide Hat, Black Frame",
     "Portrait of a bearded man in a broad-brimmed hat with a feathered collar. Charcoal on paper, signed "
     "lower right. Presented in a black moulded frame under glass."),
25: ("Watercolour Landscape with River, Boat and Deer, Slim Gilt Frame",
     "River landscape with a moored boat, figures and spotted deer at the water's edge. Watercolour on "
     "paper, signed lower left. Presented in a slim gilt frame under glass."),
26: ("Persian School Miniature, Palace Interior Scene, Navy Mat, Gilt Frame",
     "Palace interior with a mounted figure and attendant courtiers, painted in gouache and gold on paper "
     "in the Persian miniature tradition. Presented with a navy mat in a gilt frame under glass."),
27: ("Chinese Ink Painting of a Black Horse, Formosa Painting House Label No. 141",
     "Ink painting of a horse on a gold ground with a red artist's seal. Retailer label to the reverse: "
     "Formosa Painting House, No. 141. Presented in a gilt frame under glass. Horizontal format."),
28: ("Chinese Ink Painting of a Black Horse, Formosa Painting House Label No. 124",
     "Ink painting of a horse on a gold ground with a red artist's seal. Retailer label to the reverse: "
     "Formosa Painting House, No. 124. Presented in a gilt frame under glass. Vertical format."),
29: ("Double-Sided Embroidered Panel, Tigers and Leopards, Carved Black Frame",
     "Silk embroidered panel worked on both faces: two tigers on one side, a leopard and cub on the other. "
     "Presented in a carved and pierced black frame, glazed to both sides so that either face may be "
     "displayed."),
30: ("Floral Still Life Oil on Canvas, Signed W. Petitchot, Unframed",
     "W. PETITCHOT. Still life of mixed flowers in a vase against a dark ground, oil on canvas, signed "
     "lower right. Unframed, on stretcher."),
31: ("Sunflower Still Life Oil on Canvas, Unframed",
     "Still life of sunflowers in a vase with fruit on a draped table. Oil on canvas, signed lower right. "
     "Unframed, on stretcher."),
32: ("Cubist Style Oil on Canvas, Two Figures, Signed D.W. Westcott, Unframed",
     "D.W. WESTCOTT. Cubist composition of two figures, one holding a heart, oil on canvas, signed lower "
     "right. Unframed, on stretcher."),
33: ("Still Life with Sunflowers and Fruit, Oil on Canvas, Unframed",
     "Still life of sunflowers, apples and a white cloth on a table. Oil on canvas, signed lower right. "
     "Unframed, on stretcher."),
34: ("Modern Oil on Canvas, Three Women at a Table, Signed G. Roddell, Unframed",
     "G. RODDELL. Three seated women at a table in red and green dress, oil on canvas, signed lower right. "
     "Unframed, on stretcher."),
35: ("Red Flowers in a Vase, Oil on Canvas, Signed, Unframed",
     "K. LOMBARD. Still life of red flowers in a vase on a table, oil on canvas, signed lower right. "
     "Unframed, on stretcher."),
36: ("Giraffe Print with Wide Mat in Carved Gilt Frame",
     "Print of a giraffe against a pale ground, pencil inscribed in the paper margin. Presented with a "
     "wide mat in a carved gilt frame under glass."),
37: ("Watercolour of a City Square with Equestrian Monument, Linen Mat, Wood Frame",
     "City square with an equestrian monument and surrounding architecture. Watercolour on paper, signed "
     "lower left. Presented with a linen mat and inner fillet in a wood frame under glass."),
38: ("Watercolour of a Snow-Covered Cabin, Signed, Burgundy Frame",
     "Winter scene of a timber cabin among bare trees. Watercolour on paper, signed lower right. Presented "
     "with a wide white mat in a burgundy wood frame under glass."),
39: ("French Croix de Guerre avec Palme Diploma, 90th Infantry Division, 1946",
     "Diplôme de Croix de Guerre avec Palme issued by the Association Nationale des Croix de Guerre, des "
     "T.O.E. et de la Valeur Militaire. Awarded to MAC CARTHY, 370th Infantry Regiment, 90th Infantry "
     "Division, for the action of 10 to 15 November 1944 at Metz and Thionville. Décision N° 267, Paris, "
     "July 1946. Bearing the 1914-1918 and 1939-1945 medallions. Framed under glass."),
40: ("Engraving 'Campanile U.C.', Pencil Titled and Signed, Slim Black Frame",
     "'Campanile U.C.'. Engraving of a bell tower and stone archway, pencil titled and signed in the lower "
     "margin. Presented with a mat in a slim black frame under glass."),
41: ("Watercolour of a Cathedral and Market Square, Cream Mat, Wood Frame",
     "Cathedral seen across a market square with figures and a horse-drawn cart. Watercolour on paper, "
     "signed lower right. Presented with a cream mat in a wood frame under glass."),
42: ("Still Life of White Flowers, Carved Antique Gold Frame",
     "Still life of white and mauve flowers, faintly signed at the right. Presented in a carved and gilded "
     "antique frame under glass."),
43: ("Pastel of a City at Night in Blue and Yellow, Silvered Frame",
     "Night view of a city in blue and yellow pastel, with pencil annotations to the mat. Presented in a "
     "grey silvered frame under glass."),
44: ("Cubist Musicians, Layered Shadowbox Print, Black Frame",
     "Cubist composition of musicians, printed and cut in layers within a shadowbox. Presented in a deep "
     "black frame under glass."),
45: ("Susan Thomas Underwood 'The Spirits Speak To Me', Signed and Numbered",
     "SUSAN THOMAS UNDERWOOD 'The Spirits Speak To Me'. Figurative portrait, pencil titled, numbered from "
     "an edition of 200 and signed in the lower margin. Artist's statement label affixed to the reverse. "
     "Presented in a dark and gilt frame under glass."),
46: ("Colourful Print of a Woman in a Cowboy Hat, Green Mat, White Frame",
     "Portrait of a woman in a yellow shirt and cowboy hat against a desert ground. Print on paper with a "
     "printed signature. Presented with a green mat in a white frame under glass."),
47: ("Fran Larsen 'The Village Path' Watercolour, Hand Carved Polychrome Frame, 1996",
     "FRAN LARSEN 'The Village Path', 1996. Watercolour on Strathmore Crescent board, glazed with acrylic "
     "gloss medium and varnish, in a hand carved and painted polychrome frame. Titled and catalogued "
     "F 9701-006 on the label to the reverse. Framed size 21.5 by 26 inches."),
48: ("Salvador Dalí 'Piccarda Donati' Signed Print with Certificate of Authenticity",
     "SALVADOR DALI (Spanish, 1904-1989) 'Piccarda Donati'. Print in colours, pencil signed lower right "
     "with edition notation lower left. Certificate of authenticity affixed to the reverse. Presented with "
     "a burgundy fillet mat in a gilt rope-twist frame under glass."),
49: ("Sunflower Still Life Oil on Canvas Signed Legas, Carved Gold Frame",
     "LEGAS (Hungarian). Still life of yellow sunflowers in a vase, oil on canvas, signed lower right. "
     "Stretcher label 'Section No. 907-C-7, Finish Ref. 20\" x 24\", Made in Belgium'. Handwritten note to "
     "the reverse. Presented in a carved baroque gold frame."),
}
