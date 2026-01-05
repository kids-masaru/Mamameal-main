"use client";

import { useState, useEffect } from "react";
import { Upload, CheckCircle, AlertCircle, ArrowLeft, Settings, FileText } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { motion } from "framer-motion";
import API_URL from "@/lib/config";

export default function MastersPage() {
    const [productFile, setProductFile] = useState<File | null>(null);
    const [customerFile, setCustomerFile] = useState<File | null>(null);
    const [status, setStatus] = useState({ product: "", customer: "" });
    const [loading, setLoading] = useState({ product: false, customer: false });
    const [currentMasters, setCurrentMasters] = useState({ product: "読み込み中...", customer: "読み込み中..." });

    // Fetch current master file info on mount
    useEffect(() => {
        fetchMasterInfo();
    }, []);

    const fetchMasterInfo = async () => {
        try {
            const res = await axios.get(`${API_URL}/api/masters/info`);
            setCurrentMasters({
                product: res.data.product,
                customer: res.data.customer
            });
        } catch (err) {
            console.error("Failed to fetch master info:", err);
            setCurrentMasters({ product: "取得エラー", customer: "取得エラー" });
        }
    };

    const handleUpload = async (type: "product" | "customer", file: File | null) => {
        if (!file) return;

        setLoading(prev => ({ ...prev, [type]: true }));
        setStatus(prev => ({ ...prev, [type]: "" }));

        const formData = new FormData();
        formData.append("file", file);

        try {
            await axios.post(`${API_URL}/api/masters/upload?type=${type}`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setStatus(prev => ({ ...prev, [type]: "success" }));
            alert(`${type === "product" ? "商品" : "得意先"}マスタを更新しました！`);
            // Refresh master info after upload
            fetchMasterInfo();
        } catch (err: any) {
            console.error(err);
            setStatus(prev => ({ ...prev, [type]: "error" }));
            alert(`エラー: ${err.response?.data?.detail || "更新に失敗しました"}`);
        } finally {
            setLoading(prev => ({ ...prev, [type]: false }));
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-6">
            <div className="max-w-3xl mx-auto">
                <Link href="/" className="inline-flex items-center text-gray-500 hover:text-gray-900 mb-8 transition-colors">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    ダッシュボードに戻る
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-3xl shadow-sm border border-gray-100 p-8"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <h1 className="text-2xl font-bold text-gray-900">マスタ管理</h1>
                        <Settings className="w-6 h-6 text-gray-400" />
                    </div>
                    <p className="text-gray-500 mb-6">最新のマスタデータをアップロードしてください。</p>

                    {/* Current Master Info */}
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-8">
                        <h3 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
                            <FileText className="w-5 h-5" />
                            現在使用中のマスタ
                        </h3>
                        <div className="grid gap-2 text-sm">
                            <div className="flex justify-between items-center bg-white rounded-lg p-3">
                                <span className="text-gray-600">商品マスタ:</span>
                                <span className="font-medium text-blue-700">{currentMasters.product}</span>
                            </div>
                            <div className="flex justify-between items-center bg-white rounded-lg p-3">
                                <span className="text-gray-600">得意先マスタ:</span>
                                <span className="font-medium text-blue-700">{currentMasters.customer}</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid gap-6 md:grid-cols-2">
                        {/* Product Master */}
                        <div className="p-6 border rounded-2xl bg-gray-50 border-gray-200">
                            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                商品マスタ
                                {status.product === "success" && <CheckCircle className="w-4 h-4 text-green-500" />}
                                {status.product === "error" && <AlertCircle className="w-4 h-4 text-red-500" />}
                            </h3>
                            <p className="text-xs text-gray-500 mb-4">ファイル名に「商品マスタ一覧」を含めてください</p>

                            <div className="space-y-3">
                                <input
                                    type="file"
                                    accept=".csv"
                                    onChange={(e) => setProductFile(e.target.files?.[0] || null)}
                                    className="block w-full text-sm text-slate-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-orange-50 file:text-orange-700
                    hover:file:bg-orange-100"
                                />
                                <button
                                    onClick={() => handleUpload("product", productFile)}
                                    disabled={!productFile || loading.product}
                                    className="w-full py-2 px-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                                >
                                    {loading.product ? "更新中..." : "更新する"}
                                </button>
                            </div>
                        </div>

                        {/* Customer Master */}
                        <div className="p-6 border rounded-2xl bg-gray-50 border-gray-200">
                            <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                得意先マスタ
                                {status.customer === "success" && <CheckCircle className="w-4 h-4 text-green-500" />}
                                {status.customer === "error" && <AlertCircle className="w-4 h-4 text-red-500" />}
                            </h3>
                            <p className="text-xs text-gray-500 mb-4">ファイル名に「得意先マスタ一覧」を含めてください</p>

                            <div className="space-y-3">
                                <input
                                    type="file"
                                    accept=".csv"
                                    onChange={(e) => setCustomerFile(e.target.files?.[0] || null)}
                                    className="block w-full text-sm text-slate-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-indigo-50 file:text-indigo-700
                    hover:file:bg-indigo-100"
                                />
                                <button
                                    onClick={() => handleUpload("customer", customerFile)}
                                    disabled={!customerFile || loading.customer}
                                    className="w-full py-2 px-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                                >
                                    {loading.customer ? "更新中..." : "更新する"}
                                </button>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
