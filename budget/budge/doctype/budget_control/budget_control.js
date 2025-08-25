// Copyright (c) 2025, ahmed and contributors
// For license information, please see license.txt
frappe.ui.form.on('Budget Control', {
    refresh(frm) {
                // Add Report Button
        if (frm.doc.cost_center && frm.doc.department){  
            frm.add_custom_button(__('📊 Generate Report'), function() {
                show_report_dialog(frm);
            }, __('Budget Tools'));

            frm.add_custom_button(__('🗑️ Delete Budget'), function() {
                frappe.confirm(
                    __('Are you sure you want to delete this Budget?'),
                    function() {
                        // ✅ If confirmed
                        delete_budget_monthly_distribution(frm);
                    },
                    function() {
                        // ❌ If cancelled
                        frappe.show_alert({message: __('Action Cancelled'), indicator: 'blue'});
                    }
                );
            }, __('Actions'));
            // Add custom CSS for the dashboard
            // ==============================================================================
            // if (!$('#budget-dashboard-styles').length) {
            //     $('head').append(`
            //         <style id="budget-dashboard-styles">
            //             .budget-dashboard {
            //                 font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            //                 // background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            //                 //   background: linear-gradient(135deg, #0066cc 0%, ##0066cc 100%);
            //                 background :#0066cc;
            //                 border-radius: 20px;
            //                 padding: 30px;
            //                 margin: 20px 0;
            //                 color: white;
            //                 box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
            //                 position: relative;
            //                 overflow: hidden;
            //             }
                        
            //             .budget-dashboard::before {
            //                 content: '';
            //                 position: absolute;
            //                 top: -50%;
            //                 right: -50%;
            //                 width: 200%;
            //                 height: 200%;
            //                 background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            //                 pointer-events: none;
            //                 animation: float 6s ease-in-out infinite;
            //             }
                        
            //             @keyframes float {
            //                 0%, 100% { transform: translateY(0px) rotate(0deg); }
            //                 50% { transform: translateY(-20px) rotate(5deg); }
            //             }
                        
            //             .budget-header {
            //                 text-align: center;
            //                 margin-bottom: 30px;
            //                 position: relative;
            //                 z-index: 2;
            //             }
                        
            //             .budget-title {
            //                 font-size: 2.5rem;
            //                 font-weight: 800;
            //                 margin: 0;
            //                 text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            //                 background: linear-gradient(45deg, #fff, #f0f8ff);
            //                 -webkit-background-clip: text;
            //                 -webkit-text-fill-color: transparent;
            //                 background-clip: text;
            //             }
                        
            //             .budget-subtitle {
            //                 font-size: 1.1rem;
            //                 opacity: 0.9;
            //                 margin: 10px 0;
            //                 font-weight: 300;
            //             }
                        
            //             .filter-section {
            //                 background: rgba(255, 255, 255, 0.1);
            //                 backdrop-filter: blur(10px);
            //                 border-radius: 15px;
            //                 padding: 20px;
            //                 margin-bottom: 20px;
            //                 position: relative;
            //                 z-index: 2;
            //                 border: 1px solid rgba(255, 255, 255, 0.2);
            //             }
                        
            //             .filter-section .form-control {
            //                 background: rgba(255, 255, 255, 0.2);
            //                 border: 1px solid rgba(255, 255, 255, 0.3);
            //                 color: white;
            //                 border-radius: 8px;
            //             }
                        
            //             .filter-section .form-control::placeholder {
            //                 color: rgba(255, 255, 255, 0.7);
            //             }
                        
            //             .filter-section .form-control:focus {
            //                 background: rgba(255, 255, 255, 0.3);
            //                 border-color: rgba(255, 255, 255, 0.5);
            //                 box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
            //             }
                        
            //             .budget-stats {
            //                 display: grid;
            //                 // grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            //                 grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            //                 gap: 20px;
            //                 margin: 30px 0;
            //                 position: relative;
            //                 z-index: 2;
            //             }
                        
            //             .stat-card {
            //                 background: rgba(255, 255, 255, 0.15);
            //                 backdrop-filter: blur(10px);
            //                 border-radius: 15px;
            //                 padding: 20px;
            //                 text-align: center;
            //                 border: 1px solid rgba(255, 255, 255, 0.2);
            //                 transition: all 0.3s ease;
            //             }
                        
            //             .stat-card:hover {
            //                 transform: translateY(-5px);
            //                 background: rgba(255, 255, 255, 0.2);
            //                 box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            //             }
                        
            //             .stat-icon {
            //                 font-size: 2.5rem;
            //                 margin-bottom: 10px;
            //                 filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
            //             }
                        
            //             .stat-value {
            //                 // font-size: 1.8rem;
            //                 font-size: 1.2rem;
            //                 // font-weight: 700;
            //                 font-weight: 500;
            //                 margin: 5px 0;
            //             }
                        
            //             .stat-label {
            //                 font-size: 0.9rem;
            //                 opacity: 0.8;
            //                 text-transform: uppercase;
            //                 letter-spacing: 1px;
            //             }
                        
            //             .budget-items {
            //                 display: grid;
            //                 gap: 20px;
            //                 position: relative;
            //                 z-index: 2;
            //             }
                        
            //             .budget-item {
            //                 background: rgba(255, 255, 255, 0.1);
            //                 backdrop-filter: blur(15px);
            //                 border-radius: 20px;
            //                 padding: 25px;
            //                 border: 1px solid rgba(255, 255, 255, 0.2);
            //                 transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            //                 position: relative;
            //                 overflow: hidden;
            //             }
                        
            //             .budget-item::before {
            //                 content: '';
            //                 position: absolute;
            //                 top: 0;
            //                 left: -100%;
            //                 width: 100%;
            //                 height: 100%;
            //                 background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            //                 transition: left 0.5s;
            //             }
                        
            //             .budget-item:hover::before {
            //                 left: 100%;
            //             }
                        
            //             .budget-item:hover {
            //                 transform: scale(1.02);
            //                 background: rgba(255, 255, 255, 0.15);
            //                 box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            //             }
                        
            //             .item-header {
            //                 display: flex;
            //                 justify-content: space-between;
            //                 align-items: center;
            //                 margin-bottom: 20px;
            //                 flex-wrap: wrap;
            //                 gap: 10px;
            //             }
                        
            //             .item-month {
            //                 font-size: 1.5rem;
            //                 font-weight: 700;
            //                 display: flex;
            //                 align-items: center;
            //                 gap: 10px;
            //             }
                        
            //             .status-badge {
            //                 padding: 8px 16px;
            //                 border-radius: 25px;
            //                 font-size: 0.8rem;
            //                 font-weight: 600;
            //                 text-transform: uppercase;
            //                 letter-spacing: 1px;
            //                 box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            //             }
                        
            //             .status-good { background: rgba(34, 197, 94, 0.9); }
            //             .status-warning { background: rgba(251, 191, 36, 0.9); }
            //             .status-danger { background: rgba(239, 68, 68, 0.9); }
                        
            //             .item-details {
            //                 display: grid;
            //                 // grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            //                   grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            //                 gap: 15px;
            //                 margin-bottom: 20px;
            //             }
                        
            //             .detail-item {
            //                 background: rgba(0, 0, 0, 0.1);
            //                 padding: 15px;
            //                 border-radius: 12px;
            //                 border-left: 4px solid rgba(255, 255, 255, 0.3);
            //             }
                        
            //             .detail-label {
            //                 font-size: 0.8rem;
            //                 opacity: 0.7;
            //                 text-transform: uppercase;
            //                 letter-spacing: 1px;
            //                 margin-bottom: 5px;
            //             }
                        
            //             .detail-value {
            //                 font-size: 1.1rem;
            //                 font-weight: 600;
            //                 word-break: break-all;
            //             }
                        
            //             .progress-section {
            //                 margin-top: 20px;
            //             }
                        
            //             .progress-info {
            //                 display: flex;
            //                 justify-content: space-between;
            //                 align-items: center;
            //                 margin-bottom: 10px;
            //                 flex-wrap: wrap;
            //                 gap: 10px;
            //             }
                        
            //             .progress-label {
            //                 font-weight: 600;
            //                 font-size: 0.9rem;
            //             }
                        
            //             .progress-percentage {
            //                 font-size: 1.2rem;
            //                 font-weight: 700;
            //             }
                        
            //             .modern-progress {
            //                 width: 100%;
            //                 height: 12px;
            //                 background: rgba(255, 255, 255, 0.2);
            //                 border-radius: 10px;
            //                 overflow: hidden;
            //                 position: relative;
            //                 box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
            //             }
                        
            //             .progress-fill {
            //                 height: 100%;
            //                 border-radius: 10px;
            //                 transition: all 1s cubic-bezier(0.4, 0, 0.2, 1);
            //                 position: relative;
            //                 overflow: hidden;
            //             }
                        
            //             .progress-fill::after {
            //                 content: '';
            //                 position: absolute;
            //                 top: 0;
            //                 left: 0;
            //                 right: 0;
            //                 bottom: 0;
            //                 background: linear-gradient(45deg, 
            //                     rgba(255,255,255,0.2) 25%, 
            //                     transparent 25%, 
            //                     transparent 50%, 
            //                     rgba(255,255,255,0.2) 50%, 
            //                     rgba(255,255,255,0.2) 75%, 
            //                     transparent 75%);
            //                 background-size: 20px 20px;
            //                 animation: progress-animation 1s linear infinite;
            //             }
            //             .std-form-layout > .form-layout > .form-page{
                        
            //                 background: #0066cc;
            //             }
            //             .control-label{
            //                 color: var(--white);
            //             }    
            //             .form-section .section-head.collapsible, .form-dashboard-section .section-head.collapsible {
            //                 cursor: pointer;
            //                 color: var(--alert-bg-danger);
            //             }
            //             @keyframes progress-animation {
            //                 0% { background-position: 0 0; }
            //                 100% { background-position: 20px 0; }
            //             }
                        
            //             .progress-good { 
            //                 background: linear-gradient(135deg, #10b981, #059669);
            //                 box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            //             }
            //             .progress-warning { 
            //                 background: linear-gradient(135deg, #f59e0b, #d97706);
            //                 box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
            //             }
            //             .progress-danger { 
            //                 background: linear-gradient(135deg, #ef4444, #dc2626);
            //                 box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
            //             }
                        
            //             .budget-table {
            //                 background: rgba(255, 255, 255, 0.1);
            //                 backdrop-filter: blur(10px);
            //                 border-radius: 15px;
            //                 padding: 20px;
            //                 margin-top: 20px;
            //                 position: relative;
            //                 z-index: 2;
            //                 border: 1px solid rgba(255, 255, 255, 0.2);
            //             }
                        
            //             .budget-table table {
            //                 background: transparent;
            //                 color: white;
            //             }
                        
            //             .budget-table th {
            //                 background: rgba(255, 255, 255, 0.2);
            //                 border-color: rgba(255, 255, 255, 0.3);
            //                 color: white;
            //                 font-weight: 600;
            //             }
                        
            //             .budget-table td {
            //                 border-color: rgba(255, 255, 255, 0.2);
            //                 background: rgba(255, 255, 255, 0.05);
            //             }
                        
            //             .budget-table .form-control {
            //                 background: rgba(255, 255, 255, 0.2);
            //                 border: 1px solid rgba(255, 255, 255, 0.3);
            //                 color: white;
            //                 border-radius: 6px;
            //             }
                        
            //             .budget-table .form-control:focus {
            //                 background: rgba(255, 255, 255, 0.3);
            //                 border-color: rgba(255, 255, 255, 0.5);
            //                 color: white;
            //             }
                        
            //             .amount-controls {
            //                 background: rgba(255, 255, 255, 0.1);
            //                 backdrop-filter: blur(10px);
            //                 border-radius: 10px;
            //                 padding: 15px;
            //                 margin-bottom: 15px;
            //                 border: 1px solid rgba(255, 255, 255, 0.2);
            //             }
                        
            //             .no-data {
            //                 text-align: center;
            //                 padding: 60px 20px;
            //                 position: relative;
            //                 z-index: 2;
            //             }
                        
            //             .no-data-icon {
            //                 font-size: 4rem;
            //                 margin-bottom: 20px;
            //                 opacity: 0.6;
            //             }
                        
            //             .no-data-text {
            //                 font-size: 1.3rem;
            //                 font-weight: 300;
            //                 opacity: 0.8;
            //             }
                        
            //             @media (max-width: 768px) {
            //                 .budget-dashboard { padding: 20px; }
            //                 .budget-title { font-size: 2rem; }
            //                 .item-header { flex-direction: column; align-items: flex-start; }
            //                 .item-details { grid-template-columns: 1fr; }
            //                 .progress-info { flex-direction: column; align-items: flex-start; }
            //                 .filter-section { flex-direction: column; }
            //                 .filter-section > * { width: 100% !important; }
            //             }
            //         </style>
            //     `);
            // }
            // ==============================================================================
                if (!$('#budget-dashboard-styles').length) {
                    $('head').append(`
                        <style id="budget-dashboard-styles">
                            .budget-dashboard {
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
                                background: var(--bg-color, #f8f9fa);
                                border-radius: 8px;
                                padding: 24px;
                                margin: 16px 0;
                                color: var(--text-color, #374151);
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                                border: 1px solid var(--border-color, #e5e7eb);
                                position: relative;
                                overflow: hidden;
                            }
                            
                            .budget-dashboard::before {
                                content: '';
                                position: absolute;
                                top: 0;
                                left: 0;
                                right: 0;
                                height: 3px;
                                background: linear-gradient(90deg, var(--primary-color, #10b981) 0%, var(--success-color, #059669) 100%);
                                border-radius: 8px 8px 0 0;
                            }
                            
                            .budget-header {
                                text-align: left;
                                margin-bottom: 24px;
                                position: relative;
                                z-index: 2;
                                border-bottom: 1px solid var(--border-color, #e5e7eb);
                                padding-bottom: 16px;
                            }
                            
                            .budget-title {
                                font-size: 1.875rem;
                                font-weight: 600;
                                margin: 0;
                                color: var(--heading-color, #111827);
                                line-height: 1.2;
                                text-align: center;
                            }
                            
                            .budget-subtitle {
                                font-size: 0.875rem;
                                color: var(--text-muted, #6b7280);
                                margin: 4px 0 0 0;
                                font-weight: 400;
                                text-align: center;
                            }
                            
                            .filter-section {
                                background: var(--card-bg, #ffffff);
                                border-radius: 6px;
                                padding: 16px;
                                margin-bottom: 20px;
                                position: relative;
                                z-index: 2;
                                border: 1px solid var(--border-color, #e5e7eb);
                            }
                            
                            .filter-section .form-control {
                                background: var(--input-bg, #ffffff);
                                border: 1px solid var(--input-border, #d1d5db);
                                color: var(--text-color, #374151);
                                border-radius: 4px;
                                font-size: 13px;
                                padding: 4px 12px;
                                transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
                            }
                            
                            .filter-section .form-control::placeholder {
                                color: var(--text-muted, #9ca3af);
                            }
                            
                            .filter-section .form-control:focus {
                                background: var(--input-bg, #ffffff);
                                border-color: var(--primary-color, #10b981);
                                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
                                outline: none;
                            }
                            
                            .budget-stats {
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 16px;
                                margin: 24px 0;
                                position: relative;
                                z-index: 2;
                            }
                            
                            .stat-card {
                                background: var(--card-bg, #ffffff);
                                border-radius: 6px;
                                padding: 20px;
                                text-align: center;
                                border: 1px solid var(--border-color, #e5e7eb);
                                transition: all 0.2s ease;
                                position: relative;
                            }
                            
                            .stat-card:hover {
                                border-color: var(--primary-light, #d1fae5);
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                            }
                            
                            .stat-icon {
                                font-size: 2rem;
                                margin-bottom: 12px;
                                color: var(--primary-color, #10b981);
                            }
                            
                            .stat-value {
                                font-size: 1.5rem;
                                font-weight: 600;
                                margin: 8px 0;
                                color: var(--heading-color, #111827);
                            }
                            
                            .stat-label {
                                font-size: 0.8125rem;
                                color: var(--text-muted, #6b7280);
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                font-weight: 500;
                            }
                            
                            .budget-items {
                                display: grid;
                                gap: 16px;
                                position: relative;
                                z-index: 2;
                            }
                            
                            .budget-item {
                                background: var(--card-bg, #ffffff);
                                border-radius: 6px;
                                padding: 20px;
                                border: 1px solid var(--border-color, #e5e7eb);
                                transition: all 0.2s ease;
                                position: relative;
                                overflow: hidden;
                            }
                            
                            .budget-item:hover {
                                border-color: var(--primary-light, #d1fae5);
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                            }
                            
                            .item-header {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                margin-bottom: 16px;
                                flex-wrap: wrap;
                                gap: 12px;
                                padding-bottom: 12px;
                                border-bottom: 1px solid var(--border-color, #f3f4f6);
                            }
                            
                            .item-month {
                                font-size: 1.25rem;
                                font-weight: 600;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                                color: var(--heading-color, #111827);
                            }
                            
                            .status-badge {
                                padding: 4px 12px;
                                border-radius: 4px;
                                font-size: 0.75rem;
                                font-weight: 500;
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                border: 1px solid transparent;
                            }
                            
                            .status-good { 
                                background-color: var(--success-light, #d1fae5);
                                color: var(--success-dark, #065f46);
                                border-color: var(--success-color, #10b981);
                            }
                            .status-warning { 
                                background-color: var(--warning-light, #fef3c7);
                                color: var(--warning-dark, #92400e);
                                border-color: var(--warning-color, #f59e0b);
                            }
                            .status-danger { 
                                background-color: var(--danger-light, #fee2e2);
                                color: var(--danger-dark, #991b1b);
                                border-color: var(--danger-color, #ef4444);
                            }
                            
                            .item-details {
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 12px;
                                margin-bottom: 16px;
                            }
                            
                            .detail-item {
                                background: var(--bg-light, #f9fafb);
                                padding: 12px;
                                border-radius: 4px;
                                border-left: 3px solid var(--primary-color, #10b981);
                            }
                            
                            .detail-label {
                                font-size: 0.75rem;
                                color: var(--text-muted, #6b7280);
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                margin-bottom: 4px;
                                font-weight: 500;
                            }
                            
                            .detail-value {
                                font-size: 0.9375rem;
                                font-weight: 500;
                                color: var(--text-color, #374151);
                                word-break: break-word;
                            }
                            
                            .progress-section {
                                margin-top: 16px;
                                padding-top: 16px;
                                border-top: 1px solid var(--border-color, #f3f4f6);
                            }
                            
                            .progress-info {
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                margin-bottom: 8px;
                                flex-wrap: wrap;
                                gap: 8px;
                            }
                            
                            .progress-label {
                                font-weight: 500;
                                font-size: 0.875rem;
                                color: var(--text-color, #374151);
                            }
                            
                            .progress-percentage {
                                font-size: 0.875rem;
                                font-weight: 600;
                                color: var(--heading-color, #111827);
                            }
                            
                            .modern-progress {
                                width: 100%;
                                height: 8px;
                                background: var(--progress-bg, #f3f4f6);
                                border-radius: 4px;
                                overflow: hidden;
                                position: relative;
                            }
                            
                            .progress-fill {
                                height: 100%;
                                border-radius: 4px;
                                transition: all 0.3s ease;
                                position: relative;
                                overflow: hidden;
                            }
                            
                            // .std-form-layout > .form-layout > .form-page {
                            //     background: var(--bg-color, #f8f9fa);
                            // }
                            
                            .control-label {
                                color: var(--label-color, #374151);
                                font-weight: 500;
                                font-size: 13px;
                            }
                            
                            .form-section .section-head.collapsible, 
                            .form-dashboard-section .section-head.collapsible {
                                cursor: pointer;
                                color: var(--primary-color, #10b981);
                                font-weight: 500;
                            }
                            
                            .progress-good { 
                                background: linear-gradient(90deg, var(--success-color, #10b981), var(--success-dark, #059669));
                            }
                            .progress-warning { 
                                background: linear-gradient(90deg, var(--warning-color, #f59e0b), var(--warning-dark, #d97706));
                            }
                            .progress-danger { 
                                background: linear-gradient(90deg, var(--danger-color, #ef4444), var(--danger-dark, #dc2626));
                            }
                            
                            .budget-table {
                                background: var(--card-bg, #ffffff);
                                border-radius: 6px;
                                padding: 16px;
                                margin-top: 16px;
                                position: relative;
                                z-index: 2;
                                border: 1px solid var(--border-color, #e5e7eb);
                            }
                            
                            .budget-table table {
                                background: transparent;
                                color: var(--text-color, #374151);
                                font-size: 13px;
                            }
                            
                            .budget-table th {
                                background: var(--table-header-bg, #f9fafb);
                                border-color: var(--border-color, #e5e7eb);
                                color: var(--heading-color, #111827);
                                font-weight: 500;
                                font-size: 12px;
                                padding: 8px 12px;
                            }
                            
                            .budget-table td {
                                border-color: var(--border-color, #f3f4f6);
                                background: transparent;
                                padding: 8px 12px;
                                font-size: 13px;
                            }
                            
                            .budget-table .form-control {
                                background: var(--input-bg, #ffffff);
                                border: 1px solid var(--input-border, #d1d5db);
                                color: var(--text-color, #374151);
                                border-radius: 4px;
                                font-size: 13px;
                                padding: 6px 10px;
                            }
                            
                            .budget-table .form-control:focus {
                                background: var(--input-bg, #ffffff);
                                border-color: var(--primary-color, #10b981);
                                color: var(--text-color, #374151);
                                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
                            }
                            
                            .amount-controls {
                                background: var(--card-bg, #ffffff);
                                border-radius: 6px;
                                padding: 16px;
                                margin-bottom: 12px;
                                border: 1px solid var(--border-color, #e5e7eb);
                            }
                            
                            .no-data {
                                text-align: center;
                                padding: 48px 20px;
                                position: relative;
                                z-index: 2;
                            }
                            
                            .no-data-icon {
                                font-size: 3rem;
                                margin-bottom: 16px;
                                color: var(--text-muted, #9ca3af);
                            }
                            
                            .no-data-text {
                                font-size: 1.125rem;
                                font-weight: 400;
                                color: var(--text-muted, #6b7280);
                            }
                            
                            /* Dark Mode Support */
                            [data-theme="dark"] .budget-dashboard {
                                background: var(--dark-bg-2, #1f2937);
                                color: var(--dark-text-1, #f9fafb);
                                border-color: var(--dark-border-1, #374151);
                            }
                            
                            [data-theme="dark"] .budget-header {
                                border-color: var(--dark-border-1, #374151);
                            }
                            
                            [data-theme="dark"] .budget-title {
                                color: var(--dark-text-1, #f9fafb);
                            }
                            
                            [data-theme="dark"] .filter-section,
                            [data-theme="dark"] .stat-card,
                            [data-theme="dark"] .budget-item,
                            [data-theme="dark"] .budget-table,
                            [data-theme="dark"] .amount-controls {
                                background: var(--dark-bg-3, #374151);
                                border-color: var(--dark-border-1, #4b5563);
                            }
                            
                            [data-theme="dark"] .detail-item {
                                background: var(--dark-bg-1, #111827);
                            }
                            
                            @media (max-width: 768px) {
                                .budget-dashboard { 
                                    padding: 16px; 
                                    margin: 8px 0;
                                }
                                .budget-title { 
                                    font-size: 1.5rem; 
                                    text-align: center;
                                }
                                .item-header { 
                                    flex-direction: column; 
                                    align-items: flex-start; 
                                    gap: 8px;
                                }
                                .item-details { 
                                    grid-template-columns: 1fr; 
                                }
                                .progress-info { 
                                    flex-direction: column; 
                                    align-items: flex-start; 
                                }
                                .filter-section { 
                                    flex-direction: column; 
                                }
                                .filter-section > * { 
                                    width: 100% !important; 
                                }
                                .budget-stats {
                                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                                    gap: 12px;
                                }
                            }
                        </style>
                    `);
                }


            // ==============================================================================
            // Call the server method
            frappe.call({
                method: "budget.budge.doctype.budget_control.budget_control.get_monthly_distribution_department",
                args: {
                    cost_center: frm.doc.cost_center
                },
                callback: function(r) {
                        console.log('Budget Data:', r.message);
                    if (r.message && r.message.length > 0) {
                        render_modern_budget_dashboard(frm, r.message);
                    } else {
                        render_no_data_state(frm);
                    }
                },
                error: function(r) {
                    console.error('Error loading budget data:', r);
                    render_error_state(frm, r);
                }
            });
        }  
    }
});

function render_modern_budget_dashboard(frm, items) {
    let container = frm.fields_dict.budget_html.$wrapper;
    container.empty();

    // Calculate summary statistics
    const totalBudget = items.reduce((sum, item) => sum + (item.requested || 0), 0);
    const totalSpent = items.reduce((sum, item) => sum + (item.consumed || 0), 0);
    const totalRemaining = items.reduce((sum, item) => sum + (item.remaining || 0), 0);
    const utilizationRate = totalBudget > 0 ? (totalSpent / totalBudget * 100) : 0;

    // Get unique values for filters
    const uniqueItems = [...new Set(items.map(i => i.item_code).filter(Boolean))];
    const uniqueAccounts = [...new Set(items.map(i => i.account).filter(Boolean))];
    const uniqueMonths = [...new Set(items.map(i => i.month).filter(Boolean))];

    // Create main dashboard HTML
    let html = `
        <div class="budget-dashboard">
            <div class="budget-header">
                <h1 class="budget-title">💰 Budget Control Center</h1>
                <p class="budget-subtitle">
                    <strong>${frm.doc.department || "Department"}</strong> • 
                    <strong>${frm.doc.cost_center || "N/A"}</strong>
                </p>
            </div>

            <!-- Summary Stats -->
            <div class="budget-stats">
                <div class="stat-card">
                    <div class="stat-icon">💰</div>
                    <div class="stat-value">${formatCurrency(totalBudget)}</div>
                    <div class="stat-label">Total Budget</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💸</div>
                    <div class="stat-value">${formatCurrency(totalSpent)}</div>
                    <div class="stat-label">Total Spent</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💵</div>
                    <div class="stat-value">${formatCurrency(totalRemaining)}</div>
                    <div class="stat-label">Remaining</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value">${utilizationRate.toFixed(1)}%</div>
                    <div class="stat-label">Utilization</div>
                </div>
            </div>

            <!-- Filter Section -->
            <div class="filter-section">
                <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                    <select id="filter-item-code" class="form-control input-sm" style="flex:1; min-width:150px;">
                        <option value="">All Items / جميع الأصناف</option>
                        ${uniqueItems.map(code => `<option value="${code}">${code}</option>`).join('')}
                    </select>
                
                    <select id="filter-expense-account" class="form-control input-sm" style="flex:1; min-width:150px;">
                        <option value="">All Accounts / جميع الحسابات</option>
                        ${uniqueAccounts.map(account => `<option value="${account}">${account}</option>`).join('')}
                    </select>
                
                    <select id="filter-month" class="form-control input-sm" style="flex:1; min-width:120px;">
                        <option value="">All Months / جميع الشهور</option>
                        ${uniqueMonths.map(month => `<option value="${month}">${month}</option>`).join('')}
                    </select>
                
                    <button id="apply-filters" class="btn btn-primary btn-sm">Apply / تطبيق</button>
                    <button id="reset-filters" class="btn btn-secondary btn-sm">Reset / إعادة تعيين</button>
                </div>
            </div>

            <!-- Budget Items Container -->
            <div class="budget-items" id="budget-items-container"></div>
        </div>
    `;

    container.html(html);

    // Store data globally for filtering
    frm.page_budget_items = items;

    // Initial render
    render_budget_items(frm, items);

    // Setup filter events
    setupFilterEvents(frm, items);
}

function setupFilterEvents(frm, items) {
    $("#apply-filters").off("click").on("click", function() {
        const itemCode = $("#filter-item-code").val();
        const account = $("#filter-expense-account").val();
        const month = $("#filter-month").val();

        let filtered = items.filter(row => {
            return (!itemCode || row.item_code === itemCode) &&
                   (!account || row.account === account) &&
                   (!month || row.month === month);
        });

        render_budget_items(frm, filtered);
    });

    $("#reset-filters").off("click").on("click", function() {
        $("#filter-item-code").val("");
        $("#filter-expense-account").val("");
        $("#filter-month").val("");
        render_budget_items(frm, items);
    });
}

function render_budget_items(frm, items) {
    const container = $("#budget-items-container");
    container.empty();

    if (!items || items.length === 0) {
        container.html(`
            <div style="text-align:center; padding:40px; color:rgba(255,255,255,0.8);">
                <div style="font-size:3rem; margin-bottom:20px;">🔍</div>
                <h3>No results found</h3>
                <p>Try adjusting your filter criteria</p>
            </div>
        `);
        return;
    }

    // Add table view toggle
    container.html(`
        <div style="margin-bottom:20px; text-align:center;">
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-primary btn-sm" id="view-cards">Cards View</button>
                <button type="button" class="btn btn-secondary btn-sm" id="view-table">Table View</button>
            </div>
        </div>
        <div id="budget-content"></div>
    `);

    // Default to cards view
    render_cards_view(frm, items);

    // View toggle events
    $("#view-cards").off("click").on("click", function() {
        $(this).removeClass("btn-secondary").addClass("btn-primary");
        $("#view-table").removeClass("btn-primary").addClass("btn-secondary");
        render_cards_view(frm, items);
    });

    $("#view-table").off("click").on("click", function() {
        $(this).removeClass("btn-secondary").addClass("btn-primary");
        $("#view-cards").removeClass("btn-primary").addClass("btn-secondary");
        render_table_view(frm, items);
    });
}

function render_cards_view(frm, items) {
    const contentContainer = $("#budget-content");
    contentContainer.empty();

    items.forEach(row => {
        const percent = row.requested > 0 ? ((row.consumed / row.requested) * 100) : 0;
        const { status, icon, statusClass, progressClass } = getBudgetStatus(percent);

        const html = `
            <div class="budget-item">
                <div class="item-header">
                    <div class="item-month">📅 ${row.month || 'N/A'}</div>
                    <div class="status-badge ${statusClass}">
                        ${icon} ${status}
                    </div>
                </div>

                <div class="item-details">
                    <div class="detail-item">
                        <div class="detail-label">Item Code</div>
                        <div class="detail-value">${row.item_code || 'N/A'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Expense Account</div>
                        <div class="detail-value">${row.account || 'N/A'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Monthly Budget</div>
                        <div class="detail-value">${formatCurrency(row.requested || 0)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Amount Spent</div>
                        <div class="detail-value">${formatCurrency(row.consumed || 0)}</div>
                    </div>
                </div>

                <div class="progress-section">
                    <div class="progress-info">
                        <span class="progress-label">Budget Utilization</span>
                        <span class="progress-percentage">${percent.toFixed(1)}%</span>
                    </div>
                    <div class="modern-progress">
                        <div class="progress-fill ${progressClass}" style="width: ${Math.min(percent, 100)}%"></div>
                    </div>
                    <div style="margin-top: 10px; text-align: center; opacity: 0.9;">
                        <strong>Remaining: ${formatCurrency(row.remaining || 0)}</strong>
                    </div>
                </div>

                <div style="margin-top:15px; text-align:center;">
                    <button class="btn btn-success btn-sm increase-btn" data-item='${JSON.stringify(row)}'>
                        ➕ Increase Budget
                    </button>
                    <button class="btn btn-danger btn-sm decrease-btn" data-item='${JSON.stringify(row)}'>
                        ➖ Decrease Budget
                    </button>
                </div>
            </div>
        `;

        contentContainer.append(html);
    });

    // Setup button events
    setupBudgetUpdateButtons(frm);
}

function render_table_view(frm, items) {
    const contentContainer = $("#budget-content");
    
    const tableHtml = `
        <div class="budget-table">
            <div class="amount-controls">
                <label style="margin-right:10px;">Amount to Change:</label>
                <input type="number" id="change-amount" class="form-control input-sm" value="100" min="1" step="1" style="width:120px; display:inline-block;" />
            </div>
            
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Item Code</th>
                            <th>Account</th>
                            <th>Month</th>
                            <th>Budget Amount</th>
                            <th>Spent</th>
                            <th>Remaining</th>
                            <th>Utilization %</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map((row, idx) => {
                            const percent = row.requested > 0 ? ((row.consumed / row.requested) * 100) : 0;
                            const { status, statusClass } = getBudgetStatus(percent);
                            
                            return `
                                <tr>
                                    <td>${row.item_code || 'N/A'}</td>
                                    <td>${row.account || 'N/A'}</td>
                                    <td>${row.month || 'N/A'}</td>
                                    <td>
                                        <input 
                                            type="number" 
                                            class="form-control input-sm budget-amount" 
                                            data-index="${idx}" 
                                            value="${row.requested || 0}" 
                                            min="0" 
                                            step="1"
                                            style="width:120px;"
                                        />
                                    </td>
                                    <td>${formatCurrency(row.consumed || 0)}</td>
                                    <td>${formatCurrency(row.remaining || 0)}</td>
                                    <td>
                                        <span class="status-badge ${statusClass}" style="font-size:0.7rem; padding:4px 8px;">
                                            ${percent.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-xs" role="group">
                                            <button class="btn btn-success btn-xs btn-inc" data-index="${idx}" title="Increase">➕</button>
                                            <button class="btn btn-danger btn-xs btn-dec" data-index="${idx}" title="Decrease">➖</button>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    contentContainer.html(tableHtml);

    // Setup table button events
    setupTableEvents(frm, items);
}

function setupTableEvents(frm, items) {
    // Increase button handler
    $(".btn-inc").off("click").on("click", function() {
        const idx = $(this).data("index");
        const input = $(`.budget-amount[data-index="${idx}"]`);
        const value = parseFloat(input.val()) || 0;
        const step = parseFloat($("#change-amount").val()) || 1;
        input.val(value + step);
        
        const row = items[idx];

         console.log(frm)
         console.log(row)
         console.log(value)
        update_budget_amount_direct(frm, row, value,"increase");
        // Trigger change event to update the item
        input.trigger('change');
    });

    // Decrease button handler
    $(".btn-dec").off("click").on("click", function() {
        const idx = $(this).data("index");
        const input = $(`.budget-amount[data-index="${idx}"]`);
        const value = parseFloat(input.val()) || 0;
        const step = parseFloat($("#change-amount").val()) || 1;
        input.val(Math.max(0, value - step));

        const row = items[idx];
         
        update_budget_amount_direct(frm, row, value,"decrease");
        // Trigger change event to update the item
        input.trigger('change');
    });

    // Direct input change handler
    // $(".budget-amount").off("change").on("change", function() {
    //     alert(' new function ')
    //     console.log('$(this)',$(this))
    //     // const idx = $(this).data("index");
    //     // const newAmount = parseFloat($(this).val()) || 0;
    //     // const row = items[idx];
        
    //     // if (row) {
    //     //     // Update the item data
    //     //     row.requested = newAmount;
    //     //     row.remaining = newAmount - (row.consumed || 0);
            
    //     //     // Call server method to update
    //     //     update_budget_amount_direct(frm, row, newAmount);
    //     // }
    // });
}

function setupBudgetUpdateButtons(frm) {
    $(".increase-btn").off("click").on("click", function() {
        const row = JSON.parse($(this).attr("data-item"));
        update_budget_amount(frm, row, "increase");
    });

    $(".decrease-btn").off("click").on("click", function() {
        const row = JSON.parse($(this).attr("data-item"));
        update_budget_amount(frm, row, "decrease");
    });
}

function update_budget_amount(frm, row, action) {
    frappe.prompt([
        {
            label: 'Amount to ' + action,
            fieldname: 'amount',
            fieldtype: 'Currency',
            default: 100,
            reqd: 1
        }
    ], function(values) {
        let newAmount = row.requested || 0;
        
        if (action === "increase") {
            newAmount = values.amount;
        } else {
            newAmount = Math.max(0, newAmount - values.amount);
        }
        
        update_budget_amount_direct(frm, row, newAmount, action);
    }, 'Update Budget Amount / تحديث مبلغ الميزانية');
}

function update_budget_amount_direct(frm, row, newAmount, action) {
    frappe.call({
        method: "budget.budge.doctype.budget_control.budget_control.update_budget_amount",
        args: {
            cost_center: frm.doc.cost_center,
            item_code: row.item_code,
            account: row.account,
            month: row.month,
            new_amount: newAmount,
            action: action
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: __('Budget updated successfully'),
                    indicator: 'green'
                });
                
                // Refresh the dashboard
                frm.trigger('refresh');
            } else {
                frappe.show_alert({
                    message: __('Failed to update budget: ') + (r.message.error || 'Unknown error'),
                    indicator: 'red'
                });
            }
        },
        error: function(r) {
            frappe.show_alert({
                message: __('Error updating budget: ') + (r.message || 'Server error'),
                indicator: 'red'
            });
            console.error('Budget update error:', r);
        }
    });
}

function render_no_data_state(frm) {
    const container = frm.fields_dict.budget_html.$wrapper;
    container.empty();
    
    container.html(`
        <div class="budget-dashboard">
            <div class="no-data">
                <div class="no-data-icon">📊</div>
                <div class="no-data-text">No budget data found</div>
                <p style="opacity: 0.7; margin-top: 20px;">
                    No budget data found for cost center: <strong>${frm.doc.cost_center || 'N/A'}</strong><br>
                    Please check if the cost center has monthly distributions configured.
                </p>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    Refresh / تحديث
                </button>
            </div>
        </div>
    `);
}

function render_error_state(frm, error) {
    const container = frm.fields_dict.budget_html.$wrapper;
    container.empty();
    
    container.html(`
        <div class="budget-dashboard">
            <div class="no-data">
                <div class="no-data-icon">❌</div>
                <div class="no-data-text">Error loading budget data</div>
                <p style="opacity: 0.7; margin-top: 20px;">
                    ${error.message || 'Please try refreshing the form or contact your administrator.'}
                </p>
                <div style="margin-top: 20px;">
                    <button class="btn btn-primary btn-sm" onclick="location.reload()">
                        Retry / إعادة المحاولة
                    </button>
                </div>
            </div>
        </div>
    `);
}

function getBudgetStatus(percent) {
    if (percent < 70) {
        return {
            status: 'On Track',
            icon: '🟢',
            statusClass: 'status-good',
            progressClass: 'progress-good'
        };
    } else if (percent < 90) {
        return {
            status: 'CRITICAL',
            icon: '🟡',
            statusClass: 'status-warning',
            progressClass: 'progress-warning'
        };
    } else {
        return {
            status: 'Over Budget',
            icon: '🔴',
            statusClass: 'status-danger',
            progressClass: 'progress-danger'
        };
    }
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) {
        return 'EGP 0';
    }
    
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EGP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Additional utility functions for better user experience
frappe.ui.form.on('Budget Control', {
    cost_center: function(frm) {
        // Auto-refresh when cost center changes
        if (frm.doc.cost_center) {
            frm.trigger('refresh');
        }
    },
    
    department: function(frm) {
        // Auto-refresh when department changes
        if (frm.doc.department) {
            frm.trigger('refresh');
        }
    }
});

// Add keyboard shortcuts for better UX
$(document).on('keydown', function(e) {
    // Ctrl + R to refresh budget dashboard
    if (e.ctrlKey && e.key === 'r') {
        const frm = cur_frm;
        if (frm && frm.doctype === 'Budget Control') {
            e.preventDefault();
            frm.trigger('refresh');
            frappe.show_alert({
                message: __('Budget dashboard refreshed'),
                indicator: 'blue'
            });
        }
    }
});

// *** Generate Button For Report
//  1- show_report_dialog
//  2- generate_budget_report
function load_dashboard_data(frm) {
    // Show loading state
    let container = frm.fields_dict.budget_html.$wrapper;
    container.html(`
        <div class="budget-dashboard">
            <div class="no-data">
                <div class="no-data-icon">⏳</div>
                <div class="no-data-text">Loading budget data...</div>
            </div>
        </div>
    `);

    // Call the server method
    frappe.call({
        method: "budget.budge.doctype.budget_control.budget_control.get_monthly_distribution_department",
        args: {
            cost_center: frm.doc.cost_center
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                console.log('Budget Data:', r.message);
                render_modern_budget_dashboard(frm, r.message);
            } else {
                render_no_data_state(frm);
            }
        },
        error: function(r) {
            render_error_state(frm, r);
        }
    });
}
function show_report_dialog(frm) {
    // Get unique months from current data for the dropdown
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    let dialog = new frappe.ui.Dialog({
        title: '📊 Generate Budget Report',
        size: 'large',
        fields: [
            {
                label: 'Cost Center',
                fieldname: 'cost_center',
                fieldtype: 'Link',
                options:'Cost Center',
                default: frm.doc.cost_center,
                reqd: 1,
                description: 'Enter the cost center to generate report for'
            },
            {
                label: 'Month Filter',
                fieldname: 'month',
                fieldtype: 'Select',
                options: ['All Months'].concat(months),
                default: 'All Months',
                description: 'Select specific month or all months'
            },
            {
                label: 'Report Type',
                fieldname: 'report_type',
                fieldtype: 'Select',
                options: 'Summary\nDetailed\nExport to Excel',
                default: 'Summary',
                description: 'Choose the type of report to generate'
            }
        ],
        primary_action_label: '🚀 Generate Report',
        primary_action(values) {
            generate_budget_report(frm, values);
            dialog.hide();
        },
        secondary_action_label: '❌ Cancel'
    });

    dialog.show();
}


function generate_budget_report(frm, filters) {
    // Show loading state
    frappe.show_alert({
        message: __('🔄 Generating report...'),
        indicator: 'blue'
    }, 3);

    const args = {
        cost_center: filters.cost_center
    };

    // Add month filter if not "All Months"
    if (filters.month && filters.month !== 'All Months') {
        args.month = filters.month;
    }

    frappe.call({
        method: "budget.budge.doctype.budget_control.budget_control.get_monthly_distribution_report",
        args: args,
        callback: function(r) {
            if (r.message) {
                console.log('Report Data:', r.message);
                
                if (filters.report_type === 'Export to Excel') {
                    export_to_excel(r.message, filters);
                } else {
                    show_report_modal(r.message, filters);
                }
            } else {
                frappe.msgprint({
                    title: __('No Data'),
                    message: __('No data found for the selected criteria.'),
                    indicator: 'yellow'
                });
            }
        },
        error: function(r) {
            frappe.msgprint({
                title: __('Error'),
                message: r.message || __('Failed to generate report. Please try again.'),
                indicator: 'red'
            });
        }
    });
}

function show_report_modal(report_data, filters) {
    const { data, totals } = report_data;
    
    let report_html = generate_report_html(data, totals, filters);
    
    let report_dialog = new frappe.ui.Dialog({
        title: `📊 Budget Report - ${filters.cost_center}`,
        size: 'extra-large',
        fields: [
            {
                fieldname: 'report_html',
                fieldtype: 'HTML',
                options: report_html
            }
        ],
        primary_action_label: '📥 Download PDF',
        primary_action() {
            download_report_pdf(report_html, filters);
        },
        secondary_action_label: '📊 Export Excel',
        secondary_action() {
            export_to_excel(report_data, filters);
        }
    });

    report_dialog.show();
}

function generate_report_html(data, totals, filters) {
    const reportDate = frappe.datetime.now_datetime();
    
    let html = `
        <div class="report-container" style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <div class="report-header" style="text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #e2e8f0;">
                <h1 style="color: #1e293b; margin: 0; font-size: 2.5rem; font-weight: 800;">
                    📊 Monthly Budget Distribution Report
                </h1>
                <p style="color: #64748b; margin: 10px 0; font-size: 1.1rem;">
                    <strong>Cost Center:</strong> ${filters.cost_center} | 
                    <strong>Period:</strong> ${filters.month || 'All Months'} | 
                    <strong>Generated:</strong> ${frappe.datetime.str_to_user(reportDate)}
                </p>
            </div>

            <div class="summary-stats" style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            ">
                <div class="summary-card" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
                ">
                    <h3 style="margin: 0; font-size: 2rem;">💰</h3>
                    <h2 style="margin: 10px 0; font-size: 1.5rem;">${formatCurrency(totals.total_requested)}</h2>
                    <p style="margin: 0; opacity: 0.9;">Total Budget</p>
                </div>
                <div class="summary-card" style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 10px 25px rgba(240, 147, 251, 0.3);
                ">
                    <h3 style="margin: 0; font-size: 2rem;">💸</h3>
                    <h2 style="margin: 10px 0; font-size: 1.5rem;">${formatCurrency(totals.total_consumed)}</h2>
                    <p style="margin: 0; opacity: 0.9;">Total Spent</p>
                </div>
                <div class="summary-card" style="
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);
                ">
                    <h3 style="margin: 0; font-size: 2rem;">💎</h3>
                    <h2 style="margin: 10px 0; font-size: 1.5rem;">${formatCurrency(totals.total_remaining)}</h2>
                    <p style="margin: 0; opacity: 0.9;">Remaining</p>
                </div>
                <div class="summary-card" style="
                    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 10px 25px rgba(250, 112, 154, 0.3);
                ">
                    <h3 style="margin: 0; font-size: 2rem;">📊</h3>
                    <h2 style="margin: 10px 0; font-size: 1.5rem;">${((totals.total_consumed / totals.total_requested) * 100).toFixed(1)}%</h2>
                    <p style="margin: 0; opacity: 0.9;">Usage Rate</p>
                </div>
            </div>

            <div class="detailed-table" style="background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                            <th style="padding: 20px; text-align: left; font-weight: 600;">📅 Month</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">🏷️ Item Code</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">💰 Budget</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">💸 Spent</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">💎 Remaining</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">📊 Usage</th>
                            <th style="padding: 20px; text-align: left; font-weight: 600;">🚦 Status</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.forEach((row, index) => {
        const percent = row.requested > 0 ? ((row.consumed / row.requested) * 100) : 0;
        const { status, icon } = getBudgetStatus(percent);
        const rowColor = index % 2 === 0 ? '#f8fafc' : 'white';

        html += `
            <tr style="background: ${rowColor}; transition: all 0.2s;">
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">${row.month}</td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">${row.item_code || 'N/A'}</td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">${formatCurrency(row.requested)}</td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #ef4444;">${formatCurrency(row.consumed)}</td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #10b981;">${formatCurrency(row.remaining)}</td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="
                            background: #e2e8f0;
                            border-radius: 10px;
                            height: 8px;
                            width: 60px;
                            overflow: hidden;
                        ">
                            <div style="
                                background: ${percent < 70 ? '#10b981' : percent < 90 ? '#f59e0b' : '#ef4444'};
                                height: 100%;
                                width: ${Math.min(percent, 100)}%;
                                transition: width 0.5s;
                            "></div>
                        </div>
                        <span style="font-weight: 600; font-size: 0.9rem;">${percent.toFixed(1)}%</span>
                    </div>
                </td>
                <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">
                    <span style="
                        background: ${percent < 70 ? 'rgba(16, 185, 129, 0.1)' : percent < 90 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)'};
                        color: ${percent < 70 ? '#10b981' : percent < 90 ? '#f59e0b' : '#ef4444'};
                        padding: 5px 12px;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        white-space: nowrap;
                    ">${icon} ${status}</span>
                </td>
            </tr>
        `;
    });

    html += `
                    </tbody>
                </table>
            </div>

            <div class="report-footer" style="margin-top: 30px; text-align: center; color: #64748b; font-size: 0.9rem;">
                <p>📋 This report was generated automatically by the Budget Control System</p>
                <p>🕒 Report generated on ${frappe.datetime.str_to_user(reportDate)}</p>
            </div>
        </div>
    `;

    return html;
}

function export_to_excel(report_data, filters) {
    const { data, totals } = report_data;
    
    // Create CSV content
    let csv_content = "Month,Item Code,Account,Budget,Spent,Remaining,Usage %,Status\n";
    
    data.forEach(row => {
        const percent = row.requested > 0 ? ((row.consumed / row.requested) * 100) : 0;
        const { status } = getBudgetStatus(percent);
        
        csv_content += `"${row.month}","${row.item_code || 'N/A'}","${row.account || 'N/A'}",${row.requested},${row.consumed},${row.remaining},${percent.toFixed(1)}%,"${status}"\n`;
    });
    
    // Add totals row
    csv_content += `\nTOTALS,,,${totals.total_requested},${totals.total_consumed},${totals.total_remaining},${((totals.total_consumed / totals.total_requested) * 100).toFixed(1)}%,\n`;
    
    // Create and download file
    const blob = new Blob([csv_content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Budget_Report_${filters.cost_center.replace(/[^a-z0-9]/gi, '_')}_${filters.month || 'All_Months'}_${frappe.datetime.now_date()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    frappe.show_alert({
        message: __('📥 Excel file downloaded successfully!'),
        indicator: 'green'
    }, 3);
}

function download_report_pdf(html_content, filters) {
    // Create a new window for printing
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Budget Report - ${filters.cost_center}</title>
            <style>
                @media print {
                    body { margin: 0; padding: 20px; }
                    .report-container { box-shadow: none !important; }
                }
            </style>
        </head>
        <body>
            ${html_content}
        </body>
        </html>
    `);
    printWindow.document.close();
    
    // Print the window
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
    
    frappe.show_alert({
        message: __('🖨️ Print dialog opened. You can save as PDF from there.'),
        indicator: 'blue'
    }, 5);
}


function delete_budget_monthly_distribution (frm){
    frappe.call({
        method : 'budget.budge.doctype.budget_request.budget_request.delete_budget_related_records',
        args:{
            'budget_control_name':  frm.doc.name,
        },
        callback:function(r){
            console.log('api delete budget',r.message)
        }
    })
    

}