// macOS 本地 OCR：Vision 框架，离线、无 API key、无模型账号依赖。
// 数字密集截图（数据大屏 / 后台表格 / 排行榜）优先用这个，逐字带坐标。
//
// 用法：
//   swiftc -O ocr.swift -o /tmp/ocrbin && /tmp/ocrbin <image> [langs]
//   langs 默认 "zh-Hans,en-US"
// 输出：每行 "y\tx\ttext"，按从上到下、从左到右排序；y/x 是归一化坐标（0-1，原点左下）。

import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 2 else {
    print("usage: ocrbin <image> [zh-Hans,en-US]")
    exit(2)
}
let path = args[1]
let langs = args.count >= 3 ? args[2].split(separator: ",").map(String.init) : ["zh-Hans", "en-US"]

guard let img = NSImage(contentsOfFile: path),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("load fail: \(path)")
    exit(1)
}

var lines: [(y: Double, x: Double, text: String)] = []

let request = VNRecognizeTextRequest { req, _ in
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in observations {
        guard let candidate = obs.topCandidates(1).first else { continue }
        lines.append((Double(obs.boundingBox.origin.y),
                      Double(obs.boundingBox.origin.x),
                      candidate.string))
    }
}
request.recognitionLanguages = langs
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

do {
    try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
} catch {
    print("ocr fail: \(error)")
    exit(1)
}

// 同一条水平线（y 差 < 0.006）内按 x 排序，其余按 y 从上到下。
lines.sort { a, b in
    abs(a.y - b.y) > 0.006 ? a.y > b.y : a.x < b.x
}
for line in lines {
    print(String(format: "%.3f\t%.3f\t%@", line.y, line.x, line.text))
}
