"use client";

import { useState } from "react";
import { Upload, FileDown, Loader2, ArrowLeft, Sparkles } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { motion } from "framer-motion";

export default function SealPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState("");

    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            setError("");
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError("");
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return;

        setIsLoading(true);
        setError("");
        setResult(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:8000/api/seal", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResult(response.data);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || "エラーが発生しました。バックエンドが起動しているか確認してください。");
        } finally {
            setIsLoading(false);
        }
    };

    const downloadFile = (fileData: string, filename: string) => {
        const link = document.createElement("a");
        link.href = `data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,${fileData}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-6">
            <div className="max-w-3xl mx-auto">
                <Link href="/" className="inline-flex items-center text-gray-500 hover:text-pink-500 mb-8 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    ダッシュボードに戻る
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <h1 className="text-2xl font-bold text-gray-900">シール作成</h1>
                        <span className="bg-pink-100 text-pink-600 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1">
                            <Sparkles className="w-3 h-3" /> AI Powered
                        </span>
                    </div>
                    <p className="text-gray-500 mb-8">PDFから AI が情報を読み取ります。</p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div
                            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer bg-gray-50
                ${isDragging ? 'border-pink-500 bg-pink-50 scale-[1.02]' : 'border-gray-200 hover:border-pink-300'}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                accept="application/pdf"
                                onChange={handleFileChange}
                                className="hidden"
                                id="file-upload-seal"
                            />
                            <label htmlFor="file-upload-seal" className="cursor-pointer flex flex-col items-center w-full h-full">
                                <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-pink-200 text-pink-600' : 'bg-pink-100 text-pink-500'}`}>
                                    <Upload className="w-8 h-8" />
                                </div>
                                <span className="text-gray-700 font-medium text-lg">
                                    {file ? file.name : (isDragging ? "ドロップしてアップロード" : "シールPDFを選択")}
                                </span>
                                <span className="text-gray-400 text-sm mt-1">
                                    {isDragging ? "ここでマウスを離してください" : "またはドラッグ＆ドロップ"}
                                </span>
                            </label>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={!file || isLoading}
                            className="w-full bg-pink-500 hover:bg-pink-600 text-white font-bold py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    AI 解析中...
                                </>
                            ) : (
                                "AI変換開始"
                            )}
                        </button>
                    </form>

                    {result && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            className="mt-8 pt-8 border-t border-gray-100"
                        >
                            <h3 className="font-bold text-green-600 mb-4 flex items-center">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                完了しました
                            </h3>

                            <button
                                onClick={() => downloadFile(result.file_data, result.filename)}
                                className="w-full p-4 rounded-xl border border-gray-200 hover:border-pink-500 hover:bg-pink-50 transition-all text-left flex items-center gap-4 group"
                            >
                                <div className="p-3 bg-gray-100 rounded-lg group-hover:bg-pink-200 transition-colors">
                                    <FileDown className="w-6 h-6 text-gray-600 group-hover:text-pink-700" />
                                </div>
                                <div>
                                    <div className="font-bold text-gray-800">シールデータ (Excel)</div>
                                    <div className="text-xs text-gray-400 mt-1">{result.blocks?.length || 0}件のデータを抽出</div>
                                </div>
                            </button>

                            <div className="mt-6">
                                <h4 className="font-bold text-gray-700 mb-2 text-sm">解析結果プレビュー</h4>
                                <div className="bg-gray-50 rounded-xl p-4 text-xs font-mono text-gray-600 max-h-60 overflow-y-auto">
                                    <pre>{JSON.stringify(result.blocks, null, 2)}</pre>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
