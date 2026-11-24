// ocr_pages.swift — render + OCR a page range of a PDF (or one image), Chinese-capable, no installs.
//
//   swift ocr_pages.swift <file.pdf> [firstPage] [lastPage]     // 1-indexed, inclusive
//   swift ocr_pages.swift <page.jpg|page.png>                   // single image
//
// Prints "=== page N ===" then the recognized lines, one text block per line.
// Use it to LOCATE a chapter/table/CIP page. Vision mis-recognizes common hanzi
// (的→前/韵, 营养→营乔), so read any number you are going to quote off the image itself.

import Foundation
import Vision
import AppKit
import PDFKit

func ocr(_ cgImage: CGImage) -> String {
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:]);
    let request = VNRecognizeTextRequest()
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    do { try handler.perform([request]) } catch { return "" }
    guard let results = request.results else { return "" }
    return results.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

func cgImage(ofPage page: PDFPage, scale: CGFloat = 2.0) -> CGImage? {
    let box = page.bounds(for: .mediaBox)
    let w = Int(box.width * scale), h = Int(box.height * scale)
    guard w > 0, h > 0 else { return nil }
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    return ctx.makeImage()
}

let args = CommandLine.arguments
if args.count < 2 {
    FileHandle.standardError.write("usage: swift ocr_pages.swift <file.pdf> [first] [last] | <image>\n".data(using: .utf8)!)
    exit(2)
}
let path = (args[1] as NSString).expandingTildeInPath

if let doc = PDFDocument(url: URL(fileURLWithPath: path)) {
    let total = doc.pageCount
    let first = max(1, args.count > 2 ? (Int(args[2]) ?? 1) : 1)
    let last = min(total, args.count > 3 ? (Int(args[3]) ?? total) : total)
    FileHandle.standardError.write("pages: \(total)\n".data(using: .utf8)!)
    for n in first...max(first, last) {
        guard let page = doc.page(at: n - 1), let img = cgImage(ofPage: page) else {
            print("=== page \(n) ===\n<cannot render>")
            continue
        }
        print("=== page \(n) ===")
        print(ocr(img))
    }
} else if let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) {
    print("=== \((path as NSString).lastPathComponent) ===")
    print(ocr(cg))
} else {
    FileHandle.standardError.write("not a readable PDF or image: \(path)\n".data(using: .utf8)!)
    exit(1)
}
