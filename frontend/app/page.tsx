"use client";

import Link from "next/link";
import { FileText, Tag, Settings, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
    const features = [
        {
            title: "数出表・納品書作成",
            description: "PDFから注文情報を抽出し、Excelの数出表と納品書を自動作成します。",
            icon: <FileText className="w-8 h-8 text-orange-500" />,
            href: "/order",
            color: "bg-orange-50 hover:bg-orange-100",
            border: "border-orange-200",
        },
        {
            title: "シール作成",
            description: "AIを使用してPDFからシール情報を読み取り、印刷用データを作成します。",
            icon: <Tag className="w-8 h-8 text-pink-500" />,
            href: "/seal",
            color: "bg-pink-50 hover:bg-pink-100",
            border: "border-pink-200",
        },
        {
            title: "マスタ管理",
            description: "商品マスタと得意先マスタの登録・更新を行います。",
            icon: <Settings className="w-8 h-8 text-gray-500" />,
            href: "/masters",
            color: "bg-gray-50 hover:bg-gray-100",
            border: "border-gray-200",
        },
    ];

    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-4xl mx-auto px-6 py-12">
                <header className="mb-12 text-center">
                    <motion.h1
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-4xl font-bold text-gray-900 mb-4 tracking-tight"
                    >
                        Mamameal <span className="text-orange-500">Works</span>
                    </motion.h1>
                    <p className="text-gray-500">業務効率化のための統合プラットフォーム</p>
                </header>

                <div className="grid md:grid-cols-1 gap-6">
                    {features.map((feature, index) => (
                        <Link key={index} href={feature.href}>
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className={`p-6 rounded-2xl border ${feature.border} ${feature.color} transition-all duration-300 group cursor-pointer flex items-center gap-6 shadow-sm hover:shadow-md`}
                            >
                                <div className="p-4 bg-white rounded-xl shadow-sm group-hover:scale-110 transition-transform duration-300">
                                    {feature.icon}
                                </div>
                                <div className="flex-1">
                                    <h2 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-orange-600 transition-colors">
                                        {feature.title}
                                    </h2>
                                    <p className="text-gray-600 text-sm">{feature.description}</p>
                                </div>
                                <ArrowRight className="w-6 h-6 text-gray-400 group-hover:text-orange-500 group-hover:translate-x-1 transition-all" />
                            </motion.div>
                        </Link>
                    ))}
                </div>

                <footer className="mt-16 text-center text-gray-400 text-sm">
                    &copy; 2024 Mamameal Co., Ltd.
                </footer>
            </div>
        </div>
    );
}
