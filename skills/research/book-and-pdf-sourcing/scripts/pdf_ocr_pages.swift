// Render a page range of any PDF and OCR it with macOS Vision (zh-Hans + en-US).
//
//   swift pdf_ocr_pages.swift <file.pdf> [firstPage] [lastPage]
//
// Prints "=== PAGE n ===" followed by the OCR text, and writes page PNGs to
// <pdf-dir>/ocr_pages/pNNN.png. No dependencies beyond the macOS SDK — this is
// the fastest way to read a scanned Chinese book's CIP/copyright page and TOC.
//
// Fallbacks when Vision is unavailable: `pdftoppm -png -r 150 -f N -l N in.pdf out`
// (poppler) to render, then OCR however you like. Do not build a montage to read
// page text by eye — OCR the pages, the CIP line and 目录 are exact strings.

import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1 else {
    FileHandle.standardError.write("usage: swift pdf_ocr_pages.swift <file.pdf> [first] [last]\n".data(using: .utf8)!)
    exit(2)
}

let path = (args[1] as NSString).expandingTildeInPath
guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else {
    FileHandle.standardError.write("cannot open \(path)\n".data(using: .utf8)!)
    exit(1)
}

let total = doc.pageCount
let first = args.count > 2 ? max(1, Int(args[2]) ?? 1) : 1
let last = args.count > 3 ? min(total, Int(args[3]) ?? min(total, 20)) : min(total, 20)
guard first <= last, first <= total else {
    FileHandle.standardError.write("empty page range for a \(total)-page document\n".data(using: .utf8)!)
    exit(2)
}

let outDir = URL(fileURLWithPath: path)
    .deletingLastPathComponent()
    .appendingPathComponent("ocr_pages", isDirectory: true)
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

func ocr(_ cg: CGImage) -> String {
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["zh-Hans", "en-US"]
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    return (req.results ?? [])
        .compactMap { $0.topCandidates(1).first?.string }
        .joined(separator: "\n")
}

func render(_ page: PDFPage, scale: CGFloat) -> CGImage? {
    let box = page.bounds(for: .mediaBox)
    let w = Int(box.width * scale), h = Int(box.height * scale)
    guard w > 0, h > 0,
          let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
    else { return nil }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    return ctx.makeImage()
}

print("pages: \(total)  range: \(first)-\(last)")
for n in first...last {
    guard let page = doc.page(at: n - 1), let cg = render(page, scale: 150.0 / 72.0) else { continue }
    let png = outDir.appendingPathComponent(String(format: "p%03d.png", n))
    if let data = NSBitmapImageRep(cgImage: cg).representation(using: .png, properties: [:]) {
        try? data.write(to: png)
    }
    let text = ocr(cg)
    if !text.isEmpty {
        print("=== PAGE \(n) ===")
        print(text)
    }
}
