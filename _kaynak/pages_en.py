# -*- coding: utf-8 -*-
"""Static content pages, in the 1stDibs register and page set.
Every claim here describes how Visionary Object actually operates."""

# slug -> (title, eyebrow, [ (heading|None, [paragraph, ...]) ])
INFO = {
"about": ("About Us", "Our Story", [
  (None, ["Visionary Object is a single private collection of antique paintings, prints, works on "
          "paper, handmade objects and historical documents, offered directly by the person who "
          "assembled it. There is no middleman and no consignment desk: the collector answers your "
          "enquiry, quotes your shipping and packs your piece."]),
  ("One Collection, One Seller", [
    "Most marketplaces bring thousands of dealers together. We do the opposite. Every listing on "
    "this site comes from the same collection, catalogued in the same way, with the same "
    "photographs taken to the same standard.",
    "That means the condition language is consistent from one listing to the next, the reference "
    "numbers run in a single sequence, and you deal with one person from first message to delivery."]),
  ("What We Sell", [
    "Paintings and prints make up the greater part of the collection: oils, watercolours, "
    "serigraphs, etchings, engravings and lithographic posters, most of them framed as found. "
    "Alongside these are handmade objects, including hand-worked lace and embroidered panels, and "
    "historical documents such as military diplomas and certificates.",
    "Persian rugs, lighting and sculpture from the same collection are being catalogued and will be listed."]),
  ("Where We Are", [
    "The collection is held in Virginia, United States, and ships worldwide, crated and insured."]),
]),

"how-it-works": ("How It Works", "Buying", [
  (None, ["Buying here is a conversation, not a checkout queue. Five steps, and the seller is "
          "involved in all of them."]),
  ("1. Browse", ["Search by category, subject, medium, period, colour or artist. Every listing is a "
                 "single, unique piece; when it sells, it is gone."]),
  ("2. Ask", ["Use Contact Seller on any listing to request additional images, a video, a written "
              "condition report or measurements taken to your specification. Most enquiries are "
              "answered the same day."]),
  ("3. Agree a Price", ["Prices are upon request. Submit an offer with Suggest a Price and the "
                        "seller will accept, decline or counter in writing."]),
  ("4. Purchase", ["Payment is confirmed in writing before anything is packed. An order may be "
                   "cancelled free of charge within twenty-four hours of confirmation."]),
  ("5. Delivery", ["Framed work travels crated. Works on paper travel flat, between boards. Every "
                   "shipment is insured for its full agreed value and tracked to your door."]),
]),

"promise": ("The Visionary Object Promise", "Buyer Protection", [
  (None, ["Six commitments that apply to every item on this site, without exception."]),
  ("Authenticity Guaranteed", [
    "Signatures, edition numbers, back labels, gallery stamps and certificates are photographed and "
    "published with the listing. What is legible is transcribed; what is not is left blank rather "
    "than guessed at. If a piece is later shown not to be what the listing said it was, your money "
    "is returned in full, with no time limit."]),
  ("Money Back Guarantee", [
    "If the piece that arrives is not as described, return it for a full refund. A return may be "
    "initiated within 14 days of delivery."]),
  ("Price Matching", [
    "Find the same piece offered for less elsewhere and we will match the price."]),
  ("A Seller You Can Reach", [
    "One named collector, one inbox, typical response time the same day. Not a queue."]),
  ("24-Hour Cancellation", [
    "An order may be cancelled free of charge within twenty-four hours of confirmation, for any "
    "reason or none."]),
  ("Protected Global Delivery", [
    "Every shipment is crated or boarded as the piece requires, insured for its full agreed value, "
    "and tracked. If it is damaged in transit, we handle the claim, not you."]),
]),

"shipping": ("Shipping & Delivery", "Support", [
  (None, ["Shipping is quoted per item once we know the destination, because a 26-inch framed "
          "watercolour and an unframed canvas do not travel the same way."]),
  ("How Your Piece Travels", [
    "Framed work is crated: corner protection, a float mount inside the crate, and glass taped or "
    "replaced with acrylic where the route calls for it.",
    "Works on paper travel flat between acid-free boards inside a rigid outer, never rolled unless "
    "the piece was made to be rolled.",
    "Objects and textiles are packed to order."]),
  ("Timing", [
    "Packing takes two to five working days from confirmed payment. Transit is typically five to "
    "twelve working days depending on destination and customs."]),
  ("Duties and Customs", [
    "International orders may attract import duty or VAT in the destination country. These are set "
    "by your customs authority and are payable by the buyer. We declare every shipment accurately."]),
  ("Insurance", [
    "Every shipment is insured for its full agreed value. Photograph the packaging before you open "
    "it if there is visible damage, and contact us the same day."]),
]),

"returns": ("Returns & Cancellation", "Support", [
  ("24-Hour Cancellation", [
    "An order may be cancelled free of charge within twenty-four hours of confirmation. Write to "
    "the seller and the payment is reversed in full."]),
  ("Return Policy", [
    "A return for any item may be initiated within 14 days of delivery. Contact the seller first: "
    "we will send return packing instructions and arrange the collection.",
    "The piece must come back in the packing it arrived in, in the condition it left in. Once it "
    "is received and checked, the refund is issued to the original payment method."]),
  ("Not As Described", [
    "If a piece does not match its listing, the return shipping is on us and the refund is full."]),
]),

"faq": ("Frequently Asked Questions", "Support", [
  ("Why do the listings say Price Upon Request?", [
    "Because every piece is unique and pricing depends on framing, condition and destination. Use "
    "Contact Seller or Suggest a Price on any listing and you will have a figure the same day."]),
  ("Can I see more photographs?", [
    "Yes. Every listing already carries between four and thirteen photographs. Ask and the seller "
    "will send more, including video and detail shots of anything you want to see closely."]),
  ("Are the dimensions framed or unframed?", [
    "Where dimensions are listed, the listing states which. Where they are not yet listed, ask and "
    "the seller will measure the piece to your specification and photograph the tape in place."]),
  ("Do you sell to trade and interior designers?", [
    "Yes. Write to us with your project and we will quote on the pieces you have shortlisted."]),
  ("Is the frame included?", [
    "Unless the listing says Unframed, the frame shown in the photographs is included in the sale."]),
  ("Do you ship to my country?", [
    "We ship worldwide, crated and insured. Tell us the destination and you will have a quote."]),
  ("How do I know it is authentic?", [
    "Every signature, edition number, label, stamp and certificate is photographed and published "
    "with the listing. Nothing is described that is not shown. See The Visionary Object Promise."]),
]),

"contact": ("Contact Us", "Support", [
  (None, ["One inbox, answered by the collector, typically the same day."]),
  ("For a Specific Piece", [
    "Use the Contact Seller button on that listing. The reference number travels with your message, "
    "so the reply comes back about the right item."]),
  ("For Anything Else", [
    "Shipping quotes, trade enquiries, condition reports, or a request for pieces we have not "
    "listed yet: use the form on any listing page and say so in the message."]),
  ("Where We Are", ["Virginia, United States. Viewing by appointment."]),
]),

"user-agreement": ("User Agreement", "Legal", [
  (None, ["These terms govern your use of the Visionary Object website and any purchase made "
          "through it."]),
  ("Listings", [
    "Every listing describes a single, unique item. Descriptions are prepared in good faith from "
    "the item itself and from what is legible in its own photographs. Colour reproduction varies "
    "between screens; ask for further images if colour is decisive for you."]),
  ("Orders", [
    "Submitting an offer or an enquiry does not form a contract. A sale is formed when the seller "
    "confirms the agreed price in writing and payment clears. Title passes on delivery."]),
  ("Cancellation and Returns", [
    "As set out in Returns & Cancellation: free cancellation within twenty-four hours of "
    "confirmation, and returns within 14 days of delivery."]),
  ("Liability", [
    "Our liability in respect of any item is limited to the price paid for it."]),
  ("Intellectual Property", [
    "The photographs and listing text on this site are ours. The works depicted remain the "
    "intellectual property of their creators and their estates."]),
]),

"privacy": ("Privacy Policy", "Legal", [
  (None, ["We collect as little as possible and sell none of it."]),
  ("What We Collect", [
    "What you type into an enquiry form: your name, your email address, your message, and the "
    "reference number of the item you were looking at. If you ask for a shipping quote, the "
    "destination address."]),
  ("What We Do With It", [
    "Answer you. Quote your shipping. Pack and send your order. Nothing else."]),
  ("What We Do Not Do", [
    "We do not sell or share your personal information. We do not run advertising trackers. We do "
    "not build a profile of you across other websites."]),
  ("Your Choices", [
    "Ask us to delete your correspondence and we will, unless we are required to keep a record of a "
    "completed sale."]),
]),
}

# Museum page — this is the part that is ours and not 1stDibs'
MUSEUM_ROOMS = [
 ("I", "The Rotunda", "Paintings & Prints",
  "The largest room in the collection. Oils, watercolours and works on paper, most framed as they "
  "were found, hung the way a house hangs them rather than the way a fair does.", "tablo"),
 ("II", "The Cabinet", "Handmade Objects",
  "Worked by hand and never repeated: needle lace, embroidered silk, panels made to be looked at "
  "closely and from a short distance.", "obje"),
 ("III", "The Archive", "Documents",
  "Paper that was issued rather than made to be sold. Military diplomas, certificates and awards, "
  "each one addressed to a named person on a dated day.", "belge"),
 ("IV", "The Long Gallery", "Persian Rug",
  "Being catalogued. Woven pieces from the same collection, photographed flat and by the corner, "
  "listed as each is finished.", "rugs"),
 ("V", "The Lantern Room", "Lighting",
  "Being catalogued. Lamps and fittings, photographed lit and unlit.", "lighting"),
]
