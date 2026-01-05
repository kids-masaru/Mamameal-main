"use client";

import { useState } from "react";
import { Upload, FileDown, Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { motion } from "framer-motion";
import API_URL from "@/lib/config";

export default function OrderPage() {
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
            // Use 127.0.0.1 to avoid localhost IPv6 issues
            const response = await axios.post(`${API_URL}/api/order-invoice`, formData, {
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
        link.href = `data:application/vnd.ms-excel.sheet.macroEnabled.12;base64,${fileData}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const downloadXlsx = (fileData: string, filename: string) => {
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
                <Link href="/" className="inline-flex items-center text-gray-500 hover:text-orange-500 mb-8 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    ダッシュボードに戻る
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8"
                >
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">数出表・納品書作成</h1>
                    <p className="text-gray-500 mb-8">注文PDFをアップロードしてください。</p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div
                            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer bg-gray-50 
                ${isDragging ? 'border-orange-500 bg-orange-50 scale-[1.02]' : 'border-gray-200 hover:border-orange-300'}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                accept="application/pdf"
                                onChange={handleFileChange}
                                className="hidden"
                                id="file-upload"
                            />
                            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center w-full h-full">
                                <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-orange-200 text-orange-600' : 'bg-orange-100 text-orange-500'}`}>
                                    <Upload className="w-8 h-8" />
                                </div>
                                <span className="text-gray-700 font-medium text-lg">
                                    {file ? file.name : (isDragging ? "ドロップしてアップロード" : "PDFファイルを選択")}
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
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                    処理中...
                                </>
                            ) : (
                                "変換開始"
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
                            <div className="grid gap-4 md:grid-cols-2">
                                <button
                                    onClick={() => downloadFile(result.template_file.data, result.template_file.filename)}
                                    className="p-4 rounded-xl border border-gray-200 hover:border-orange-500 hover:bg-orange-50 transition-all text-left flex items-start gap-4 group"
                                >
                                    <div className="p-3 bg-gray-100 rounded-lg group-hover:bg-orange-200 transition-colors">
                                        <FileDown className="w-6 h-6 text-gray-600 group-hover:text-orange-700" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-gray-800">数出表</div>
                                        <div className="text-xs text-gray-400 mt-1">XLSM (マクロ付)</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => downloadXlsx(result.nouhinsyo_file.data, result.nouhinsyo_file.filename)}
                                    className="p-4 rounded-xl border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-all text-left flex items-start gap-4 group"
                                >
                                    <div className="p-3 bg-gray-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                                        <FileDown className="w-6 h-6 text-gray-600 group-hover:text-blue-700" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-gray-800">納品書</div>
                                        <div className="text-xs text-gray-400 mt-1">XLSX</div>
                                    </div>
                                </button>
                            </div>
                        </motion.div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
